from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.logger import get_logger, setup_logging
from src.db_manager import DatabaseManager
import src.dk_pools as dk_pools

setup_logging()
logger = get_logger(__name__)

class PoolScheduler:
    """Manages automatic data ingestion scheduling."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self, update_interval_hours=4):
        """
        Start the scheduler with periodic data ingestion.
        
        Args:
            update_interval_hours: Interval in hours between updates (default: 4)
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule data ingestion to run every N hours
            self.scheduler.add_job(
                func=self._run_data_ingestion,
                trigger=IntervalTrigger(hours=update_interval_hours),
                id='pool_ingestion',
                name='DFS Pool Data Ingestion',
                replace_existing=True,
                max_instances=1
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Scheduler started with {update_interval_hours}h update interval")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def _run_data_ingestion(self):
        """Execute the data ingestion process."""
        try:
            logger.info("Starting scheduled data ingestion...")
            dk_pools.main()
            
            # Update sports_inventory table after data ingestion
            logger.info("Updating sports inventory...")
            db = DatabaseManager()
            db.update_sports_inventory()
            logger.info("Sports inventory updated successfully")
            
            logger.info("Scheduled data ingestion completed successfully")
        except Exception as e:
            logger.error(f"Error during scheduled data ingestion: {e}")

# Global scheduler instance
pool_scheduler = PoolScheduler()