import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Singleton configuration class for application settings"""
    _instance: Optional['Config'] = None
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize configuration with environment variables"""
        # Load environment variables
        load_dotenv()
        
        # MongoDB settings
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.mongodb_db = os.getenv('MONGODB_DB')
        self.collection_faq = os.getenv('COLLECTION_FAQ')
        self.collection_nav = os.getenv('COLLECTION_NAV')
        
        # OpenAI settings
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_API_MODEL')
        
        # Application settings
        self.app_name = "FixConnect FAQ Database"
        self.app_version = "1.0"