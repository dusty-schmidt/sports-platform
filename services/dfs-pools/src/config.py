import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True") == "True"
    SCHEDULER_INTERVAL_HOURS = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "4"))
    
    DATABASE_PATH = os.getenv("DATABASE_PATH", "dfs_pools.db")
    
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))
    API_DEBUG = os.getenv("API_DEBUG", "False") == "True"
    
    DRAFTKINGS_SPORTS_ENDPOINT = "https://api.draftkings.com/sites/US-DK/sports/v1/sports?format=json"
    DRAFTKINGS_CONTESTS_ENDPOINT = "https://www.draftkings.com/lobby/getcontests?sport={sport}"
    DRAFTKINGS_DRAFTABLES_ENDPOINT = "https://api.draftkings.com/draftgroups/v1/draftgroups/{draftgroup_id}/draftables"
    
    VALID_GAME_TYPES = ["Classic", "Showdown Captain Mode"]
    TENNIS_VALID_GAME_TYPES = ["Classic", "Showdown Captain Mode", "Single Game"]
    
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    REQUEST_RETRY_COUNT = int(os.getenv("REQUEST_RETRY_COUNT", "3"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))
    
    SAVE_JSON_BACKUPS = os.getenv("SAVE_JSON_BACKUPS", "False") == "True"
    JSON_BACKUP_DIR = os.getenv("JSON_BACKUP_DIR", "data/draftables")
    SAVE_BACKUP_FOR_UPCOMING_ONLY = os.getenv("SAVE_BACKUP_FOR_UPCOMING_ONLY", "True") == "True"
    
    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        errors = []
        
        if cls.SCHEDULER_INTERVAL_HOURS <= 0:
            errors.append("SCHEDULER_INTERVAL_HOURS must be greater than 0")
        
        if cls.API_PORT < 1 or cls.API_PORT > 65535:
            errors.append("API_PORT must be between 1 and 65535")
        
        if cls.REQUEST_TIMEOUT <= 0:
            errors.append("REQUEST_TIMEOUT must be greater than 0")
        
        if cls.REQUEST_RETRY_COUNT < 0:
            errors.append("REQUEST_RETRY_COUNT must be non-negative")
        
        if cls.REQUEST_DELAY < 0:
            errors.append("REQUEST_DELAY must be non-negative")
        
        return errors


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG_MODE = True
    LOG_LEVEL = "DEBUG"
    API_DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG_MODE = False
    LOG_LEVEL = "WARNING"
    API_DEBUG = False
    SCHEDULER_ENABLED = True


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG_MODE = True
    LOG_LEVEL = "DEBUG"
    API_DEBUG = True
    DATABASE_PATH = ":memory:"
    SCHEDULER_ENABLED = False


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class


config = get_config()