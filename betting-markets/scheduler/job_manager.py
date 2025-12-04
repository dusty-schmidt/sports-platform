"""Job manager for scheduling and managing betting market data collection jobs."""

from __future__ import annotations

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from betting_service.service import BettingMarketService
from database import get_db, BettingMarketDBService
from scheduler.config import config, get_sport_config

# Create the scheduler instance
scheduler = AsyncIOScheduler()

LOGGER = logging.getLogger(__name__)


class JobManager:
    """Manages scheduled jobs for betting market data collection."""
    
    def __init__(self):
        self.active_jobs: Dict[str, str] = {}  # sport -> job_id
        self.job_stats: Dict[str, Dict] = {}  # sport -> stats
    
    async def start_scheduler(self):
        """Start the scheduler and add default jobs."""
        try:
            # Add cleanup job
            self.add_cleanup_job()
            
            # Add auto-collection jobs for configured sports
            for sport in config.auto_collect_sports:
                await self.add_sport_job(sport)
            
            # Start the scheduler
            if not scheduler.running:
                scheduler.start()
            
            LOGGER.info("Scheduler started with %d sport jobs", len(config.auto_collect_sports))
            
        except Exception as e:
            LOGGER.error("Failed to start scheduler: %s", e)
            raise
    
    async def stop_scheduler(self):
        """Stop the scheduler."""
        try:
            scheduler.shutdown(wait=False)
            LOGGER.info("Scheduler stopped")
        except Exception as e:
            LOGGER.error("Failed to stop scheduler: %s", e)
    
    async def add_sport_job(self, sport: str) -> bool:
        """Add a job for collecting data for a specific sport."""
        try:
            sport_config = get_sport_config(sport)
            interval_minutes = sport_config["interval_minutes"]
            books = sport_config["books"]
            
            # Create job ID
            job_id = f"collect_{sport}"
            
            # Remove existing job if present
            if job_id in scheduler.get_jobs():
                scheduler.remove_job(job_id)
                LOGGER.info("Removed existing job for %s", sport)
            
            # Add new job
            trigger = IntervalTrigger(minutes=interval_minutes)
            scheduler.add_job(
                func=self._run_collection_job,
                trigger=trigger,
                id=job_id,
                name=f"Collect {sport.upper()} data",
                args=[sport, books],
                max_instances=1,  # Prevent concurrent runs
                coalesce=True,    # Skip missed runs
                misfire_grace_time=300  # 5 minutes grace period
            )
            
            self.active_jobs[sport] = job_id
            LOGGER.info("Added job for %s (interval: %d minutes)", sport, interval_minutes)
            
            return True
            
        except Exception as e:
            LOGGER.error("Failed to add job for %s: %s", sport, e)
            return False
    
    async def remove_sport_job(self, sport: str) -> bool:
        """Remove the job for a specific sport."""
        try:
            job_id = self.active_jobs.get(sport)
            if not job_id:
                LOGGER.warning("No job found for sport %s", sport)
                return False
            
            if job_id in scheduler.get_jobs():
                scheduler.remove_job(job_id)
                LOGGER.info("Removed job for %s", sport)
            
            del self.active_jobs[sport]
            if sport in self.job_stats:
                del self.job_stats[sport]
            
            return True
            
        except Exception as e:
            LOGGER.error("Failed to remove job for %s: %s", sport, e)
            return False
    
    def get_active_jobs(self) -> List[Dict]:
        """Get list of currently active jobs."""
        jobs = []
        for job in scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger),
                "args": job.args
            }
            jobs.append(job_info)
        return jobs
    
    def get_job_status(self, sport: str) -> Optional[Dict]:
        """Get status of a specific sport's job."""
        return self.job_stats.get(sport)
    
    async def _run_collection_job(self, sport: str, books: List[str]):
        """Internal method to run a data collection job."""
        job_start_time = datetime.utcnow()
        
        try:
            LOGGER.info("Starting data collection job for %s", sport)
            
            # Update job stats
            self.job_stats[sport] = {
                "last_run": job_start_time,
                "status": "running",
                "events_collected": 0,
                "error": None
            }
            
            # Get database session
            db = next(get_db())
            try:
                db_service = BettingMarketDBService(db)
                
                # Create and run collection service
                collection_service = BettingMarketService(sport, books=books)
                events = collection_service.collect()
                
                if events:
                    # Store events in database
                    snapshots = db_service.store_market_events(events)
                    
                    # Update stats
                    self.job_stats[sport].update({
                        "status": "completed",
                        "events_collected": len(events),
                        "snapshots_created": len(snapshots),
                        "duration_seconds": (datetime.utcnow() - job_start_time).total_seconds()
                    })
                    
                    LOGGER.info("Successfully collected %d events for %s", len(events), sport)
                else:
                    self.job_stats[sport].update({
                        "status": "completed",
                        "events_collected": 0,
                        "snapshots_created": 0,
                        "duration_seconds": (datetime.utcnow() - job_start_time).total_seconds()
                    })
                    LOGGER.info("No events found for %s", sport)
            
            finally:
                db.close()
                
        except Exception as e:
            error_msg = str(e)
            LOGGER.error("Data collection job failed for %s: %s", sport, error_msg)
            
            # Update job stats with error
            self.job_stats[sport].update({
                "status": "failed",
                "error": error_msg,
                "duration_seconds": (datetime.utcnow() - job_start_time).total_seconds()
            })
    
    def add_cleanup_job(self):
        """Add a job to clean up old data."""
        # Run cleanup daily at 2 AM
        trigger = CronTrigger(hour=2, minute=0)
        scheduler.add_job(
            func=self._run_cleanup_job,
            trigger=trigger,
            id="daily_cleanup",
            name="Daily data cleanup",
            max_instances=1,
            coalesce=True
        )
        LOGGER.info("Added daily cleanup job")
    
    async def _run_cleanup_job(self):
        """Run cleanup job to remove old snapshots."""
        try:
            LOGGER.info("Starting daily cleanup job")
            
            db = next(get_db())
            try:
                db_service = BettingMarketDBService(db)
                deleted_count = db_service.cleanup_old_snapshots(config.days_to_keep_snapshots)
                LOGGER.info("Cleanup job completed: deleted %d old snapshots", deleted_count)
            finally:
                db.close()
                
        except Exception as e:
            LOGGER.error("Cleanup job failed: %s", e)
    
    async def trigger_manual_collection(self, sport: str, books: Optional[List[str]] = None) -> Dict:
        """Manually trigger collection for a sport."""
        try:
            # Use default books if none specified
            if books is None:
                sport_config = get_sport_config(sport)
                books = sport_config["books"]
            
            LOGGER.info("Manual collection triggered for %s", sport)
            
            # Run collection synchronously (blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: asyncio.run(self._run_collection_job(sport, books))
            )
            
            # Get updated stats
            stats = self.get_job_status(sport)
            
            return {
                "sport": sport,
                "books": books,
                "status": "triggered",
                "stats": stats
            }
            
        except Exception as e:
            LOGGER.error("Manual collection failed for %s: %s", sport, e)
            return {
                "sport": sport,
                "books": books,
                "status": "failed",
                "error": str(e)
            }
    
    def get_scheduler_stats(self) -> Dict:
        """Get overall scheduler statistics."""
        jobs = self.get_active_jobs()
        
        return {
            "scheduler_running": scheduler.running,
            "active_jobs": len(jobs),
            "job_details": jobs,
            "job_statistics": self.job_stats,
            "config": {
                "auto_collect_sports": config.auto_collect_sports,
                "cleanup_interval_hours": config.cleanup_interval_hours,
                "days_to_keep_snapshots": config.days_to_keep_snapshots
            }
        }


# Global job manager instance
job_manager = JobManager()