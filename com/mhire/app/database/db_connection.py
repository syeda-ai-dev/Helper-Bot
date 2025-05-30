import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from com.mhire.app.config.config import Config

logger = logging.getLogger(__name__)

class DBConnection:
    """Database connection manager"""
    
    def __init__(self):
        self.config = Config()
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        
        try:
            # Initialize MongoDB client
            self.client = AsyncIOMotorClient(
                self.config.mongodb_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            self.db = self.client[self.config.mongodb_db]
            logger.info("MongoDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            raise
    
    async def ping(self) -> bool:
        """Check if MongoDB server is reachable"""
        try:
            await self.client.admin.command('ping')
            logger.info("MongoDB ping successful")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB ping failed: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the MongoDB connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed successfully")
                
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
            raise