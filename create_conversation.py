import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL_AUTH = "https://auth-staging.thesis.io/api"
BASE_URL_BACKEND = "https://backend-beta.thesis.io/api"
SPACE_ID = "402"
CONVERSATION_SPACE_ID = "402"
AUTH_HEADERS = {
    "x-device-id": "5e73524bfcb95a64886ded5c99f0776f",
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMjE1IiwicHVibGljQWRkcmVzcyI6IjB4NjhkZmQyZGY5NDBmMDdhODI0ODU3ZmMzYzFjNzYyZmE3MjQwZWMyNCIsInN0YXR1cyI6MSwid2hpdGVsaXN0ZWQiOjEsInN1Ym9yZ0lkIjoiNjZmNmVkY2QtNmViOS00MjFlLWE0MDctNjMzN2Y0MTkwZDIyIiwiYXV0aDBJZCI6InR3aXR0ZXJ8MTU1Mzk1MzU5MTgyODA0MTcyOSJ9LCJpYXQiOjE3NTQ1NDk1ODAsImV4cCI6MTc1NDcyMjM4MH0.fwo99k50jcepE-1xtK3PU-KCQjMLFqlU2HQvUpxseaA",
}
CONVERSATION_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMjE1IiwicHVibGljQWRkcmVzcyI6IjB4NjhkZmQyZGY5NDBmMDdhODI0ODU3ZmMzYzFjNzYyZmE3MjQwZWMyNCIsInN0YXR1cyI6MSwid2hpdGVsaXN0ZWQiOjEsInN1Ym9yZ0lkIjoiNjZmNmVkY2QtNmViOS00MjFlLWE0MDctNjMzN2Y0MTkwZDIyIiwiYXV0aDBJZCI6InR3aXR0ZXJ8MTU1Mzk1MzU5MTgyODA0MTcyOSJ9LCJpYXQiOjE3NTQ1NDk1ODAsImV4cCI6MTc1NDcyMjM4MH0.fwo99k50jcepE-1xtK3PU-KCQjMLFqlU2HQvUpxseaA",
    "content-type": "application/json",
    "x-device-id": "5e73524bfcb95a64886ded5c99f0776f",
}


async def create_conversation(
    session: aiohttp.ClientSession,
    initial_user_msg: str,
    system_prompt: str = None,
    image_urls: list = None,
    research_mode: str = "deep_research",
    space_id: str = None,
) -> Dict[str, Any]:
    """Create a new conversation using the backend API."""
    url = f"{BASE_URL_BACKEND}/conversations"

    payload = {
        "initial_user_msg": initial_user_msg,
        "image_urls": image_urls,
        "system_prompt": system_prompt,
        "mcp_disable": {},
        "research_mode": research_mode,
        "space_id": space_id,
    }

    logger.info(f"Creating conversation with message: {initial_user_msg[:50]}...")
    logger.debug(f"Request URL: {url}")
    logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

    try:
        async with session.post(
            url, headers=CONVERSATION_HEADERS, json=payload
        ) as response:
            response_text = await response.text()
            logger.info(f"Create conversation response status: {response.status}")
            logger.debug(f"Create conversation response body: {response_text}")

            if response.status == 200:
                try:
                    response_data = json.loads(response_text)
                    logger.info("Conversation created successfully")
                    return response_data
                except json.JSONDecodeError:
                    logger.warning("Response is not valid JSON, but status is 200")
                    return {"status": "success", "raw_response": response_text}
            else:
                logger.error(
                    f"Failed to create conversation: {response.status} - {response_text}"
                )
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=response_text,
                )

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise


async def create_batch_conversation(
    messages: list[str], space_id: str = None
) -> Dict[str, Any]:
    """Create a batch of conversations using the backend API."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            create_conversation(session, message, space_id=space_id)
            for message in messages
        ]
        results = await asyncio.gather(*tasks)
        await session.close()
        return results
