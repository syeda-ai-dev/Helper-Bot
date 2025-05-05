import os
import logging
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Environment variables
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
        self.MODEL = os.getenv("MODEL")
        self.DB_URL = os.getenv("DB_URL")  # Add DB_URL
        
        # Other config variables can be added here
        self.APP_NAME = "Helper Bot"
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
        
        # Setup logging configuration
        self.setup_logging()
        # Setup other configurations if needed
    
    def setup_logging(self):
        # Configure logging for the application
        log_level = logging.DEBUG if self.DEBUG else logging.INFO
        
        # Configure the root logger
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        # Set specific loggers to different levels if needed
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.INFO)
    
    def get_logger(self, name=None):
        # Get a logger with the specified name
        return logging.getLogger(name)

# Create a global instance
config = Config()

def get_settings():
    """Return the config instance."""
    return config