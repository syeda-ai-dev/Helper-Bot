import logging
from typing import Optional, Dict, Any
import openai
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from com.mhire.app.config.config import Config
from com.mhire.app.database.db_manager import DBManager
from com.mhire.app.services.helper_bot.helper_bot_schema import ChatResponse, UserType

logger = logging.getLogger(__name__)

class HelperBot:
    """Helper bot service for handling user queries with FAQ and LLM support"""
    
    def __init__(self):
        try:
            # Initialize config singleton
            self.config = Config()
            if not self.config.openai_api_key or not self.config.openai_model:
                logger.error("OpenAI configuration missing")
                raise ValueError("OpenAI configuration missing")
            
            # Initialize database manager
            self.db_manager = DBManager()
            
            # Configure OpenAI
            openai.api_key = self.config.openai_api_key
            
            # Initialize LangChain components
            self.llm = ChatOpenAI(
                model_name=self.config.openai_model,
                temperature=0.7,
                max_tokens=300
            )
            
            # Define prompt template
            self.prompt = PromptTemplate(
                input_variables=["context", "query", "faq_results"],
                template="""You are a helpful support agent for FixConnect app.
                Context: {context}
                User Query: {query}
                FAQ Results: {faq_results}

Instructions:
1. If FAQ matches are provided above, check each one carefully to find the most relevant answer.
2. If you find a matching FAQ answer, use it EXACTLY as written - do not modify it.
3. Only generate a new answer if none of the FAQ answers are relevant to the query.
4. Your response should be clear and concise (1-2 sentences).
5. Do not include any formatting or prefixes (like "Answer:", "Response:", etc.).
6. Focus on answering the exact question asked.

Return your response now:"""
            )
            
            # Create response chain
            self.chain = (
                self.prompt
                | self.llm
                | StrOutputParser()
            )
            
        except Exception as e:
            logger.error(f"HelperBot initialization failed: {str(e)}")
            raise

    async def get_response(self, query: str, user_type: UserType) -> ChatResponse:
        """Get response from FAQ or LLM with improved FAQ prioritization"""
        try:
            # Search FAQ first
            faq_results = await self.db_manager.search_faq(query, user_type)
            
            # Log all FAQ results for debugging
            logger.info(f"Query: '{query}' | User type: {user_type.value} | Found {len(faq_results) if faq_results else 0} FAQ results")
            if faq_results:
                for i, faq in enumerate(faq_results):
                    logger.info(f"FAQ #{i+1}: Q: '{faq.get('question', '')}' | Score: {faq.get('textScore', 0) or faq.get('score', 0):.2f}")
            
            # If we have any FAQ matches, prioritize them based on confidence
            if faq_results and len(faq_results) > 0:
                best_match = faq_results[0]
                best_score = best_match.get("textScore", 0) or best_match.get("score", 0)
                
                # High confidence match (exact or near-exact)
                if best_score >= 1.5:
                    logger.info(f"Using high confidence FAQ match: {best_score:.2f}")
                    return ChatResponse(
                        message=best_match["answer"],
                        source="faq",
                        confidence_score=min(best_score / 3, 1.0)  # Normalize score
                    )
                
                # Medium confidence match
                if best_score >= 0.8:
                    logger.info(f"Using medium confidence FAQ match: {best_score:.2f}")
                    return ChatResponse(
                        message=best_match["answer"],
                        source="faq",
                        confidence_score=min(best_score / 3, 0.9)  # Normalize score
                    )
                
                # Lower confidence but still usable match
                if best_score >= 0.5:
                    logger.info(f"Using lower confidence FAQ match: {best_score:.2f}")
                    return ChatResponse(
                        message=best_match["answer"],
                        source="faq",
                        confidence_score=min(best_score / 3, 0.7)  # Normalize score
                    )
            
            # Format FAQ results for LLM context
            faq_context = "Available FAQ matches:\n" if faq_results else "No FAQ matches found."
            if faq_results:
                for faq in faq_results:
                    faq_context += f"Question: {faq['question']}\nAnswer: {faq['answer']}\nScore: {faq.get('textScore', 0) or faq.get('score', 0):.2f}\n\n"
            
            # Log that we're falling back to LLM
            logger.info(f"No suitable FAQ match found for '{query}', falling back to LLM")
            
            # Generate LLM response
            try:
                # Calculate a dynamic confidence score for LLM responses
                # If we have low-scoring FAQ matches, the LLM confidence should be lower
                llm_confidence = 0.4  # Base confidence for LLM
                if faq_results and len(faq_results) > 0:
                    best_score = faq_results[0].get("textScore", 0) or faq_results[0].get("score", 0)
                    # If we have FAQ results with scores close to our threshold, reduce LLM confidence
                    if best_score >= 0.3:
                        llm_confidence = 0.3
                
                llm_response = await self.chain.ainvoke({
                    "context": "No suitable FAQ match found, generating a response.",
                    "query": query,
                    "faq_results": faq_context
                })
                
                logger.info(f"Generated LLM response with confidence: {llm_confidence:.2f}")
                
                return ChatResponse(
                    message=llm_response,
                    source="gpt",
                    confidence_score=llm_confidence
                )
                
            except Exception as e:
                logger.error(f"LLM response generation failed: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            raise