import os
from dotenv import load_dotenv
            
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Face++ API settings
            cls._instance.openai_api_key = os.getenv("OPENAI_API_KEY")
            cls._instance.openai_model = os.getenv("OPENAI_API_MODEL")
            
            # MongoDB settings
            cls._instance.mongodb_uri = os.getenv("MONGODB_URI")
            cls._instance.mongodb_db = os.getenv("MONGODB_DB")
            cls._instance.mongodb_collection = os.getenv("MONGODB_COLLECTION")

        return cls._instance