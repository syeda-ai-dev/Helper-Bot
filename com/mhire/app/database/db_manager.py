import logging
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import TEXT
from fuzzywuzzy import fuzz

from com.mhire.app.database.db_connection import DBConnection
from com.mhire.app.services.helper_bot.helper_bot_schema import UserType

logger = logging.getLogger(__name__)

class DBManager(DBConnection):
    """Database manager for FAQ operations"""
    
    def __init__(self):
        super().__init__()
        try:
            self.faq_collection: AsyncIOMotorCollection = self.db[self.config.collection_faq]
        except Exception as e:
            logger.error(f"Failed to initialize FAQ collection: {str(e)}")
            raise
    
    async def search_faq(self, query: str, user_type: UserType) -> List[Dict[Any, Any]]:
        """Search FAQ with improved matching using MongoDB aggregation pipeline"""
        try:
            # Define the aggregation pipeline
            pipeline = [
                # Unwind the nested arrays
                {"$unwind": "$categories"},
                {"$unwind": "$categories.questions"},
                
                # Match documents for the correct user type
                {"$match": {"categories.questions.user_type": user_type.value}},
                
                # Add text search score with multiple matching strategies
                {"$addFields": {
                    "textScore": {
                        "$cond": [
                            # Exact match (case insensitive)
                            {"$eq": [{"$toLower": "$categories.questions.question_text"}, {"$toLower": query}]},
                            3.0,  # Highest score for exact matches
                            {"$cond": [
                                # Contains the entire query as a substring
                                {"$regexMatch": {
                                    "input": "$categories.questions.question_text",
                                    "regex": query,
                                    "options": "i"
                                }},
                                2.0,  # High score for containing the query
                                # Contains keywords from the query
                                {"$cond": [
                                    {"$or": [
                                        {"$regexMatch": {
                                            "input": "$categories.questions.question_text",
                                            "regex": query.split(" ")[0] if len(query.split(" ")) > 0 else query,
                                            "options": "i"
                                        }},
                                        {"$regexMatch": {
                                            "input": "$categories.questions.answer_text",
                                            "regex": query,
                                            "options": "i"
                                        }}
                                    ]},
                                    1.0,  # Medium score for keyword matches
                                    0.5    # Low score for everything else
                                ]}
                            ]}
                        ]
                    }
                }},
                
                # Sort by score
                {"$sort": {"textScore": -1}},
                
                # Limit results
                {"$limit": 3},
                
                # Project the needed fields
                {"$project": {
                    "question": "$categories.questions.question_text",
                    "answer": "$categories.questions.answer_text",
                    "category": "$categories.category_name",
                    "user_type": "$categories.questions.user_type",
                    "score": "$textScore"
                }}
            ]
            
            # Execute aggregation pipeline
            results = await self.faq_collection.aggregate(pipeline).to_list(length=3)
            
            # If no results from text search, try semantic search
            if not results:
                # Get all FAQs for user type
                all_faqs = await self.faq_collection.aggregate([
                    {"$unwind": "$categories"},
                    {"$unwind": "$categories.questions"},
                    {"$match": {"categories.questions.user_type": user_type.value}},
                    {"$project": {
                        "question": "$categories.questions.question_text",
                        "answer": "$categories.questions.answer_text",
                        "category": "$categories.category_name",
                        "user_type": "$categories.questions.user_type"
                    }}
                ]).to_list(length=None)
                
                # Calculate semantic similarity
                scored_results = []
                for faq in all_faqs:
                    # Calculate similarity scores
                    question_score = fuzz.ratio(query.lower(), faq["question"].lower())
                    keyword_score = fuzz.partial_ratio(query.lower(), faq["question"].lower())
                    answer_score = fuzz.partial_ratio(query.lower(), faq["answer"].lower())
                    
                    # Weighted scoring
                    total_score = (
                        question_score * 0.6 +  # Higher weight for exact question matches
                        keyword_score * 0.3 +   # Medium weight for partial question matches
                        answer_score * 0.1      # Lower weight for answer content matches
                    ) / 100
                    
                    if total_score > 0.5:  # Threshold for semantic matches
                        scored_results.append({
                            **faq,
                            "score": total_score
                        })
                
                # Sort by score and take top results
                results = sorted(scored_results, key=lambda x: x["score"], reverse=True)[:3]
            
            return results
            
        except Exception as e:
            logger.error(f"FAQ search failed: {str(e)}")
            raise