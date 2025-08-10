#!/usr/bin/env python3
"""
Twitter Agent - Functional style with tool-use patterns

A refactored AI-powered Twitter agent using functional approach with DSpy's ReAct framework
and Thesis conversation API. Supports only two tools: research_thesis and post_tweet.

This implementation uses polling pattern for research completion and functional style
for all operations to support proper agent tool-use.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional, List
import dspy

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration (from create_conversation.py patterns)
BASE_URL_BACKEND = "https://backend-beta.thesis.io/api"
SPACE_ID = "402"
CONVERSATION_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMjE1IiwicHVibGljQWRkcmVzcyI6IjB4NjhkZmQyZGY5NDBmMDdhODI0ODU3ZmMzYzFjNzYyZmE3MjQwZWMyNCIsInN0YXR1cyI6MSwid2hpdGVsaXN0ZWQiOjEsInN1Ym9yZ0lkIjoiNjZmNmVkY2QtNmViOS00MjFlLWE0MDctNjMzN2Y0MTkwZDIyIiwiYXV0aDBJZCI6InR3aXR0ZXJ8MTU1Mzk1MzU5MTgyODA0MTcyOSJ9LCJpYXQiOjE3NTQ1NDk1ODAsImV4cCI6MTc1NDcyMjM4MH0.fwo99k50jcepE-1xtK3PU-KCQjMLFqlU2HQvUpxseaA",
    "content-type": "application/json",
    "x-device-id": "5e73524bfcb95a64886ded5c99f0776f",
}

# Twitter configuration (mock for demonstration)
TWITTER_CONFIG = {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret",
    "bearer_token": "your_bearer_token",
}


async def research_thesis(query: str, research_mode: str = "deep_research", system_prompt: Optional[str] = None) -> str:
    """
    Research a topic using Thesis conversation API with polling pattern for completion.
    
    This tool creates a conversation for research and polls until the final result is available.
    It uses the Thesis backend API to perform deep research on any given topic.
    
    Args:
        query: The research query or topic to investigate
        research_mode: Type of research mode (default: "deep_research")
        system_prompt: Optional system prompt to guide the research
        
    Returns:
        str: The complete research content once processing is finished
        
    Tool Description for Agent:
    Use this tool to research any topic thoroughly. The tool will handle the polling
    and return comprehensive research results. Perfect for gathering information 
    before creating content or making decisions.
    """
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Create conversation
            conversation_data = await _create_conversation(
                session, query, research_mode, system_prompt
            )
            
            if "id" not in conversation_data:
                logger.warning("No conversation ID returned from Thesis API")
                return f"Research query: {query}\nNo detailed research available."
                
            conversation_id = conversation_data["id"]
            logger.info(f"Created conversation {conversation_id} for research: {query[:50]}...")
            
            # Step 2: Poll for completion using final_result endpoint
            return await _poll_for_research_completion(session, conversation_id, query)
            
        except Exception as e:
            logger.error(f"Error during research: {e}")
            return f"Research query: {query}\nError during research: {str(e)}"


def post_tweet(content: str) -> Dict[str, Any]:
    """
    Post a tweet to Twitter using the configured API credentials.
    
    This tool posts content to Twitter, automatically truncating if necessary
    to fit within Twitter's character limits.
    
    Args:
        content: The text content to post as a tweet
        
    Returns:
        Dict containing success status, tweet_id if successful, and content
        
    Tool Description for Agent:
    Use this tool to post tweets to Twitter. The tool will handle character limits
    and return confirmation of successful posting. Only use this tool when you want
    to actually publish content to the Twitter platform.
    """
    try:
        # Truncate content to fit Twitter's character limit
        if len(content) > 280:
            content = content[:277] + "..."
        
        logger.info(f"Posting tweet: {content[:50]}...")
        
        # Mock implementation - in real scenario, use tweepy or Twitter API
        # For demonstration purposes, we'll simulate a successful tweet
        import random
        tweet_id = str(random.randint(1000000000000000000, 9999999999999999999))
        
        # In a real implementation, you would use:
        # import tweepy
        # auth = tweepy.OAuthHandler(TWITTER_CONFIG["api_key"], TWITTER_CONFIG["api_secret"])
        # auth.set_access_token(TWITTER_CONFIG["access_token"], TWITTER_CONFIG["access_token_secret"])
        # api = tweepy.API(auth)
        # tweet = api.update_status(content)
        # return {"success": True, "tweet_id": tweet.id_str, "content": content}
        
        logger.info(f"Tweet posted successfully with ID: {tweet_id}")
        return {
            "success": True,
            "tweet_id": tweet_id,
            "content": content,
            "note": "This is a mock implementation - configure Twitter API credentials for real posting"
        }
        
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return {
            "success": False,
            "error": str(e),
            "content": content,
        }


async def _create_conversation(
    session: aiohttp.ClientSession,
    query: str,
    research_mode: str,
    system_prompt: Optional[str],
) -> Dict[str, Any]:
    """Create a new conversation for research."""
    url = f"{BASE_URL_BACKEND}/conversations"
    
    payload = {
        "initial_user_msg": query,
        "image_urls": None,
        "system_prompt": system_prompt,
        "mcp_disable": {},
        "research_mode": research_mode,
        "space_id": SPACE_ID,
    }
    
    logger.info(f"Creating research conversation for: {query[:50]}...")
    
    async with session.post(url, headers=CONVERSATION_HEADERS, json=payload) as response:
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


async def _poll_for_research_completion(
    session: aiohttp.ClientSession, 
    conversation_id: str, 
    original_query: str,
    max_wait_time: int = 120,
    poll_interval: int = 3
) -> str:
    """
    Poll for research completion using the final_result endpoint.
    
    This implements the polling pattern as specified in the requirements,
    using the provided API endpoint to get the final result.
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Use the final_result endpoint as specified
            url = f"{BASE_URL_BACKEND}/conversations/{conversation_id}/final_result"
            
            async with session.get(url, headers=CONVERSATION_HEADERS) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result_data = json.loads(response_text)
                        
                        # Check if research is complete
                        if result_data.get("status") == "completed" or result_data.get("final_result"):
                            logger.info(f"Research completed for conversation {conversation_id}")
                            return _extract_final_result(result_data, original_query)
                        elif result_data.get("status") == "processing":
                            logger.info(f"Research still processing... waiting {poll_interval}s")
                        else:
                            # Try to extract any available content
                            content = _extract_final_result(result_data, original_query)
                            if content and len(content) > 50:  # Substantial content found
                                return content
                                
                    except json.JSONDecodeError:
                        # If we get a plain text response, it might be the result
                        if len(response_text) > 50:
                            logger.info(f"Got text response, treating as final result")
                            return response_text
                        
                elif response.status == 404:
                    # Conversation might not be ready yet, continue polling
                    logger.debug("Conversation not ready yet, continuing to poll")
                else:
                    logger.warning(f"Unexpected status {response.status} while polling")
                    
        except Exception as e:
            logger.warning(f"Error during polling attempt: {e}")
            
        await asyncio.sleep(poll_interval)
    
    # Timeout reached - try to get whatever we can from regular conversation endpoint
    logger.warning(f"Polling timeout reached for conversation {conversation_id}")
    return await _get_conversation_fallback(session, conversation_id, original_query)


async def _get_conversation_fallback(
    session: aiohttp.ClientSession,
    conversation_id: str,
    original_query: str
) -> str:
    """Fallback method to get conversation result if polling times out."""
    url = f"{BASE_URL_BACKEND}/conversations/{conversation_id}"
    
    try:
        async with session.get(url, headers=CONVERSATION_HEADERS) as response:
            response_text = await response.text()
            
            if response.status == 200:
                try:
                    conversation_data = json.loads(response_text)
                    return _extract_research_content(conversation_data, original_query)
                except json.JSONDecodeError:
                    return response_text if response_text else f"Research query: {original_query}\nProcessing incomplete."
            else:
                logger.error(f"Failed to get conversation result: {response.status}")
                return f"Research query: {original_query}\nError retrieving results."
                
    except Exception as e:
        logger.error(f"Error in fallback method: {e}")
        return f"Research query: {original_query}\nError during research: {str(e)}"


def _extract_final_result(result_data: Dict[str, Any], original_query: str) -> str:
    """Extract the final result from the API response."""
    # Try different possible keys for the final result
    if "final_result" in result_data:
        return result_data["final_result"]
    
    if "content" in result_data:
        return result_data["content"]
        
    if "result" in result_data:
        return result_data["result"]
        
    # Try to extract from messages if available
    return _extract_research_content(result_data, original_query)


def _extract_research_content(conversation_data: Dict[str, Any], original_query: str) -> str:
    """Extract research content from conversation data (fallback method)."""
    if "messages" in conversation_data:
        messages = conversation_data["messages"]
        # Find the assistant's response
        for message in reversed(messages):
            if message.get("role") == "assistant" and message.get("content"):
                return message["content"]
    
    if "raw_response" in conversation_data:
        return conversation_data["raw_response"]
    
    return f"Research query: {original_query}\nNo research content found in response."


class SimplifiedReActAgent:
    """
    Simplified ReAct agent that uses only two tools:
    1. research_thesis - for researching topics
    2. post_tweet - for posting tweets
    
    This agent removes all redundant functions and focuses on the core functionality.
    """
    
    def __init__(self, config=None):
        """Initialize the simplified ReAct agent."""
        self.config = config or {}
        
        # Initialize DSpy if configuration is provided
        if hasattr(config, 'api_key') and hasattr(config, 'api_base') and config.api_key:
            dspy.configure(
                lm=dspy.LM(
                    api_key=config.api_key,
                    model=getattr(config, 'model', 'gpt-3.5-turbo'),
                    api_base=config.api_base,
                )
            )
        else:
            logger.warning("DSpy configuration not provided, using defaults")
        
        # Define the agent's signature for two-tool usage
        self.react_signature = dspy.Signature(
            "task -> thought, action, action_input, observation, answer"
        )
        self.react_module = dspy.ReAct(self.react_signature)
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a task using only research_thesis and post_tweet tools.
        
        Args:
            task: The task description
            
        Returns:
            Dict containing task execution results
        """
        logger.info(f"Executing simplified task: {task}")
        
        try:
            # Use ReAct to plan the task
            result = self.react_module(task=task)
            
            # Execute only allowed actions
            actions = self._parse_allowed_actions(result)
            execution_results = []
            
            for action in actions:
                action_result = await self._execute_allowed_action(action)
                execution_results.append(action_result)
            
            return {
                "task": task,
                "reasoning": getattr(result, "thought", ""),
                "actions": actions,
                "results": execution_results,
                "final_answer": getattr(result, "answer", ""),
                "success": True,
            }
            
        except Exception as e:
            logger.error(f"Error executing simplified task: {e}")
            return {
                "task": task,
                "error": str(e),
                "success": False,
            }
    
    def _parse_allowed_actions(self, result) -> List[Dict[str, Any]]:
        """
        Parse actions from ReAct result, allowing only research_thesis and post_tweet.
        """
        actions = []
        
        if hasattr(result, "action") and hasattr(result, "action_input"):
            action_type = result.action.lower()
            
            # Map various action names to our two allowed tools
            if action_type in ["research", "research_thesis", "search_research", "investigate"]:
                actions.append({
                    "action": "research_thesis",
                    "input": result.action_input,
                })
            elif action_type in ["tweet", "post_tweet", "post", "publish_tweet"]:
                actions.append({
                    "action": "post_tweet",
                    "input": result.action_input,
                })
            else:
                logger.warning(f"Action '{action_type}' not allowed. Only research_thesis and post_tweet are supported.")
        
        # If no valid actions found, default to research for information gathering tasks
        if not actions and "research" in result.task.lower():
            actions.append({
                "action": "research_thesis",
                "input": getattr(result, "task", ""),
            })
        
        return actions
    
    async def _execute_allowed_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute only allowed actions: research_thesis or post_tweet.
        """
        action_type = action["action"]
        action_input = action["input"]
        
        logger.info(f"Executing allowed action: {action_type} with input: {action_input[:50]}...")
        
        if action_type == "research_thesis":
            try:
                research_result = await research_thesis(action_input)
                return {
                    "action": "research_thesis",
                    "query": action_input,
                    "result": research_result,
                    "success": True,
                }
            except Exception as e:
                return {
                    "action": "research_thesis",
                    "query": action_input,
                    "error": str(e),
                    "success": False,
                }
                
        elif action_type == "post_tweet":
            try:
                tweet_result = post_tweet(action_input)
                return {
                    "action": "post_tweet",
                    "content": action_input,
                    "result": tweet_result,
                    "success": tweet_result.get("success", False),
                }
            except Exception as e:
                return {
                    "action": "post_tweet",
                    "content": action_input,
                    "error": str(e),
                    "success": False,
                }
        else:
            return {
                "action": action_type,
                "success": False,
                "error": f"Action '{action_type}' not allowed. Only research_thesis and post_tweet are supported.",
            }
    
    async def research_and_tweet(self, topic: str) -> Dict[str, Any]:
        """
        High-level method to research a topic and create a tweet.
        Uses only the two allowed tools in sequence.
        """
        logger.info(f"Research and tweet workflow for topic: {topic}")
        
        try:
            # Step 1: Research the topic
            research_result = await research_thesis(topic)
            
            if not research_result or "Error" in research_result:
                return {
                    "task": f"research_and_tweet: {topic}",
                    "error": f"Research failed: {research_result}",
                    "success": False,
                }
            
            # Step 2: Generate tweet content from research
            # For simplicity, take first 200 characters and create engaging content
            summary = research_result[:200] + "..." if len(research_result) > 200 else research_result
            
            tweet_content = f"Interesting insights on {topic}:\n\n{summary}\n\n#Research #AI"
            
            # Ensure tweet fits in character limit
            if len(tweet_content) > 280:
                tweet_content = tweet_content[:250] + "... #Research #AI"
            
            # Step 3: Post the tweet
            tweet_result = post_tweet(tweet_content)
            
            return {
                "task": f"research_and_tweet: {topic}",
                "research_result": research_result,
                "tweet_content": tweet_content,
                "tweet_result": tweet_result,
                "success": tweet_result.get("success", False),
            }
            
        except Exception as e:
            logger.error(f"Error in research_and_tweet: {e}")
            return {
                "task": f"research_and_tweet: {topic}",
                "error": str(e),
                "success": False,
            }


async def main():
    """Main function demonstrating the simplified Twitter Agent."""
    logger.info("Twitter Agent - Simplified Functional Style with Two Tools")
    logger.info("=" * 60)
    logger.info("Tools available: research_thesis, post_tweet")
    logger.info("Polling pattern implemented for research completion")
    logger.info("=" * 60)

    try:
        # Initialize the simplified agent
        logger.info("Initializing simplified ReAct agent...")
        agent = SimplifiedReActAgent()

        # Example 1: Test research function directly
        logger.info("\nTesting research_thesis function...")
        research_topic = "artificial intelligence trends 2024"
        research_result = await research_thesis(research_topic)
        logger.info(f"Research result: {research_result[:200]}...")

        # Example 2: Test tweet function directly
        logger.info("\nTesting post_tweet function...")
        test_tweet = "Testing the new functional Twitter agent! #AI #Research"
        tweet_result = post_tweet(test_tweet)
        logger.info(f"Tweet result: {tweet_result}")

        # Example 3: Use the simplified agent for a complete workflow
        logger.info("\nTesting complete research and tweet workflow...")
        workflow_result = await agent.research_and_tweet(research_topic)
        
        if workflow_result.get("success"):
            logger.info("Workflow completed successfully!")
            
            # Display results
            research_content = workflow_result.get("research_result", "")
            if research_content:
                logger.info(f"\nResearch Summary:")
                logger.info(
                    research_content[:300] + "..."
                    if len(research_content) > 300
                    else research_content
                )
            
            tweet_content = workflow_result.get("tweet_content", "")
            tweet_result = workflow_result.get("tweet_result", {})
            if tweet_content:
                logger.info(f"\nGenerated Tweet:")
                logger.info(f"'{tweet_content}'")
                logger.info(f"Tweet ID: {tweet_result.get('tweet_id', 'N/A')}")
                logger.info("(Note: Mock implementation - configure Twitter API for real posting)")
        else:
            error = workflow_result.get("error", "Unknown error")
            logger.error(f"Workflow failed: {error}")

        # Example 4: Test agent with a research-only task
        logger.info("\nTesting agent with research-only task...")
        research_task = "Research the latest developments in quantum computing"
        task_result = await agent.execute_task(research_task)
        
        if task_result.get("success"):
            logger.info("Research task completed!")
            for result in task_result.get("results", []):
                if result.get("action") == "research_thesis":
                    logger.info(f"Research: {result.get('result', '')[:200]}...")
        
        logger.info("\nAll tests completed!")
        logger.info("Summary of refactoring:")
        logger.info("  • Converted from class-based to functional approach")
        logger.info("  • Implemented polling pattern for research completion")
        logger.info("  • Reduced to only 2 tools: research_thesis and post_tweet")
        logger.info("  • Removed all redundant functions")
        logger.info("  • Added proper tool descriptions for agent use")

    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error("\nSetup notes:")
        logger.error("   1. This uses hardcoded API tokens from create_conversation.py")
        logger.error("   2. Twitter posting is mocked - configure real credentials for posting")
        logger.error("   3. Research uses Thesis API with polling pattern as specified")


# Tool registry for agent use
TOOLS = {
    "research_thesis": {
        "function": research_thesis,
        "description": "Research any topic using Thesis API with polling for completion. Returns comprehensive research results.",
        "parameters": {
            "query": "string - The research query or topic to investigate",
            "research_mode": "string - Type of research mode (default: 'deep_research')",
            "system_prompt": "string - Optional system prompt to guide research"
        }
    },
    "post_tweet": {
        "function": post_tweet,
        "description": "Post content to Twitter with automatic character limit handling. Returns success status and tweet ID.",
        "parameters": {
            "content": "string - The text content to post as a tweet"
        }
    }
}


if __name__ == "__main__":
    asyncio.run(main())