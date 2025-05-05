import json
import os
import logging
import aiohttp
from typing import Dict, List, Any, Optional, Tuple

from mhire.com.app.services.helper_bot.helper_bot_schema import ChatResponse

logger = logging.getLogger(__name__)

class HelperBot:
    def __init__(self, openai_api_key: str, openai_endpoint: str, model: str):
        self.openai_api_key = openai_api_key
        self.openai_endpoint = openai_endpoint
        self.model = model
        self.site_map = None
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
    
    async def load_site_map(self):
        """Load the site structure map from JSON file specified in DB_URL."""
        try:
            from mhire.com.config.config import get_settings
            settings = get_settings()
            
            if not settings.DB_URL:
                raise ValueError("DB_URL not configured")
                
            with open(settings.DB_URL, 'r') as f:
                self.site_map = json.load(f)
            logger.info("Site map loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load site map: {str(e)}")
            return False
    
    def find_path_in_map(self, query: str) -> Tuple[Optional[List[str]], Optional[Dict[str, Any]]]:
        """Search the site map for content relevant to the user's query."""
        if not self.site_map:
            logger.error("Site map not loaded")
            return None, None
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Search keywords in the sitemap
        best_match = None
        best_path = None
        highest_score = 0
        
        def search_map(node, current_path=None):
            nonlocal best_match, best_path, highest_score
            
            if current_path is None:
                current_path = []
                
            # Check if this node contains keywords that match the query
            if isinstance(node, dict):
                # Calculate a simple relevance score based on keyword matches
                score = 0
                
                # Check title, description and keywords if they exist
                for field in ["title", "description", "keywords"]:
                    if field in node and isinstance(node[field], str):
                        field_text = node[field].lower()
                        if query_lower in field_text:
                            score += 3
                        for word in query_lower.split():
                            if word in field_text:
                                score += 1
                
                if score > highest_score:
                    highest_score = score
                    best_match = node
                    best_path = current_path.copy()
                
                # Recursively search child nodes
                for key, value in node.items():
                    if isinstance(value, dict):
                        search_map(value, current_path + [key])
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                search_map(item, current_path + [key, str(i)])
        
        search_map(self.site_map)
        return best_path, best_match
    
    def format_navigation_instructions(self, path: List[str], node_info: Dict[str, Any]) -> str:
        """Format clear step-by-step navigation instructions."""
        if not path or not node_info:
            return "I couldn't find specific instructions for that in our system."
        
        # Start building the navigation steps
        steps = []
        breadcrumbs = []
        
        # Navigate through the site map to build breadcrumbs
        current = self.site_map
        for segment in path:
            if segment.isdigit() and isinstance(current, list):
                idx = int(segment)
                if idx < len(current):
                    current = current[idx]
                    if "title" in current:
                        breadcrumbs.append(current["title"])
            elif segment in current:
                current = current[segment]
                if isinstance(current, dict) and "title" in current:
                    breadcrumbs.append(current["title"])
        
        # Format as steps
        nav_steps = " → ".join(breadcrumbs)
        
        # Include additional instructions if available
        instructions = ""
        if "instructions" in node_info:
            instructions = f"\n\n{node_info['instructions']}"
        
        # Include any action buttons or form fields if available
        action_info = ""
        if "actions" in node_info and node_info["actions"]:
            actions = ", ".join([f'"{a}"' for a in node_info["actions"]])
            action_info = f"\n\nAvailable actions: {actions}"
            
        if "fields" in node_info and node_info["fields"]:
            fields = ", ".join([f'"{f}"' for f in node_info["fields"]])
            action_info += f"\n\nForm fields: {fields}"
        
        return f"Go to {nav_steps}{instructions}{action_info}"
    
    async def generate_response(self, query: str) -> ChatResponse:
        """Generate a response to the user's query."""
        if not self.site_map:
            success = await self.load_site_map()
            if not success:
                return ChatResponse(
                    message="I'm sorry, I couldn't access the system information needed to help you. Please try again later.",
                    navigation_path=None
                )

        path, node_info = self.find_path_in_map(query)
        navigation_instructions = ""
        if path and node_info:
            navigation_instructions = self.format_navigation_instructions(path, node_info)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for a web application. "
                    "Provide clear step-by-step instructions when users ask how to do something. "
                    "Be concise and friendly. If specific navigation instructions are provided, "
                    "integrate them naturally into your response."
                )
            },
            {"role": "user", "content": query}
        ]

        if navigation_instructions:
            messages.append({
                "role": "system",
                "content": f"Use these specific navigation instructions in your response: {navigation_instructions}"
            })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.openai_endpoint,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        return ChatResponse(
                            message="I'm having trouble connecting to my knowledge base right now. Please try again later.",
                            navigation_path=None
                        )

                    data = await response.json()
                    ai_response = data["choices"][0]["message"]["content"]

                    return ChatResponse(
                        message=ai_response,
                        navigation_path=path
                    )

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return ChatResponse(
                message="I encountered an error while trying to help you. Please try again later.",
                navigation_path=None
            )