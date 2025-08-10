"""Thesis API integration for research functionality."""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ThesisResearcher:
    """Research assistant using Thesis conversation API."""
    
    def __init__(self, config):
        """Initialize with Thesis configuration."""
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.auth_token}",
            "content-type": "application/json",
            "x-device-id": config.device_id,
        }
    
    async def research_query(
        self,
        query: str,
        research_mode: str = "deep_research",
        system_prompt: Optional[str] = None,
    ) -> str:
        """Research a query using Thesis conversation API."""
        async with aiohttp.ClientSession() as session:
            try:
                conversation_data = await self._create_conversation(
                    session, query, research_mode, system_prompt
                )
                
                if "id" in conversation_data:
                    conversation_id = conversation_data["id"]
                    # Wait for the conversation to process
                    await asyncio.sleep(2)
                    
                    # Get the conversation result
                    result = await self._get_conversation_result(session, conversation_id)
                    return self._extract_research_content(result)
                else:
                    logger.warning("No conversation ID returned from Thesis API")
                    return f"Research query: {query}\nNo detailed research available."
                    
            except Exception as e:
                logger.error(f"Error during research: {e}")
                return f"Research query: {query}\nError during research: {str(e)}"
    
    async def _create_conversation(
        self,
        session: aiohttp.ClientSession,
        query: str,
        research_mode: str,
        system_prompt: Optional[str],
    ) -> Dict[str, Any]:
        """Create a new conversation for research."""
        url = f"{self.config.base_url_backend}/conversations"
        
        payload = {
            "initial_user_msg": query,
            "image_urls": None,
            "system_prompt": system_prompt,
            "mcp_disable": {},
            "research_mode": research_mode,
            "space_id": self.config.space_id,
        }
        
        logger.info(f"Creating research conversation for: {query[:50]}...")
        
        async with session.post(url, headers=self.headers, json=payload) as response:
            response_text = await response.text()
            
            if response.status == 200:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON response from create conversation")
                    return {"status": "success", "raw_response": response_text}
            else:
                logger.error(f"Failed to create conversation: {response.status}")
                raise Exception(f"API Error: {response.status} - {response_text}")
    
    async def _get_conversation_result(
        self,
        session: aiohttp.ClientSession,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """Get the result of a conversation."""
        url = f"{self.config.base_url_backend}/conversations/{conversation_id}"
        
        async with session.get(url, headers=self.headers) as response:
            response_text = await response.text()
            
            if response.status == 200:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"raw_response": response_text}
            else:
                logger.error(f"Failed to get conversation result: {response.status}")
                return {"error": f"API Error: {response.status}"}
    
    def _extract_research_content(self, conversation_data: Dict[str, Any]) -> str:
        """Extract research content from conversation data."""
        if "messages" in conversation_data:
            messages = conversation_data["messages"]
            # Find the assistant's response
            for message in reversed(messages):
                if message.get("role") == "assistant" and message.get("content"):
                    return message["content"]
        
        if "raw_response" in conversation_data:
            return conversation_data["raw_response"]
        
        return "No research content found in response."