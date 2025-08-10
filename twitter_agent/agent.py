"""DSpy ReAct Agent for Twitter interactions."""

import dspy
import logging
import asyncio
from typing import Dict, Any, List, Optional
from .thesis_research import ThesisResearcher
from .twitter_client import TwitterClient

logger = logging.getLogger(__name__)


class TwitterReACtAgent:
    """ReAct agent for Twitter interactions with research capabilities."""
    
    def __init__(self, twitter_client: TwitterClient, thesis_researcher: ThesisResearcher, config):
        """Initialize the ReAct agent."""
        self.twitter_client = twitter_client
        self.thesis_researcher = thesis_researcher
        self.config = config
        
        # Initialize DSpy with OpenAI
        if config.openai_api_key:
            dspy.configure(
                lm=dspy.OpenAI(
                    api_key=config.openai_api_key,
                    model=config.model,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
            )
        else:
            logger.warning("OpenAI API key not provided, using default DSpy configuration")
        
        # Define the agent's signature
        self.react_signature = dspy.Signature(
            "task -> thought, action, action_input, observation, answer"
        )
        self.react_module = dspy.ReAct(self.react_signature)
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute a task using ReAct methodology."""
        logger.info(f"Executing task: {task}")
        
        try:
            # Use ReAct to plan and execute the task
            result = self.react_module(task=task)
            
            # Process the planned actions
            actions = self._parse_actions(result)
            execution_results = []
            
            for action in actions:
                action_result = await self._execute_action(action)
                execution_results.append(action_result)
            
            return {
                "task": task,
                "reasoning": result.thought if hasattr(result, 'thought') else "",
                "actions": actions,
                "results": execution_results,
                "final_answer": result.answer if hasattr(result, 'answer') else "",
                "success": True,
            }
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                "task": task,
                "error": str(e),
                "success": False,
            }
    
    def _parse_actions(self, result) -> List[Dict[str, Any]]:
        """Parse actions from ReAct result."""
        actions = []
        
        if hasattr(result, 'action') and hasattr(result, 'action_input'):
            actions.append({
                "action": result.action,
                "input": result.action_input,
            })
        
        # If no specific actions, infer from the task
        if not actions:
            # Default to research action for most tasks
            actions.append({
                "action": "research",
                "input": getattr(result, 'task', ''),
            })
        
        return actions
    
    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action."""
        action_type = action["action"].lower()
        action_input = action["input"]
        
        logger.info(f"Executing action: {action_type} with input: {action_input}")
        
        if action_type in ["research", "search_research", "investigate"]:
            return await self._research_action(action_input)
        elif action_type in ["tweet", "post_tweet", "post"]:
            return await self._tweet_action(action_input)
        elif action_type in ["search_tweets", "search"]:
            return await self._search_tweets_action(action_input)
        elif action_type in ["get_timeline", "timeline"]:
            return await self._timeline_action(action_input)
        else:
            return {
                "action": action_type,
                "success": False,
                "error": f"Unknown action type: {action_type}",
            }
    
    async def _research_action(self, query: str) -> Dict[str, Any]:
        """Execute research action using Thesis API."""
        try:
            research_result = await self.thesis_researcher.research_query(query)
            return {
                "action": "research",
                "query": query,
                "result": research_result,
                "success": True,
            }
        except Exception as e:
            return {
                "action": "research",
                "query": query,
                "error": str(e),
                "success": False,
            }
    
    async def _tweet_action(self, content: str) -> Dict[str, Any]:
        """Execute tweet posting action."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.twitter_client.post_tweet, content
            )
            return {
                "action": "tweet",
                "content": content,
                "result": result,
                "success": result.get("success", False),
            }
        except Exception as e:
            return {
                "action": "tweet",
                "content": content,
                "error": str(e),
                "success": False,
            }
    
    async def _search_tweets_action(self, query: str) -> Dict[str, Any]:
        """Execute tweet search action."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.twitter_client.search_tweets, query, 10
            )
            return {
                "action": "search_tweets",
                "query": query,
                "result": result,
                "success": True,
            }
        except Exception as e:
            return {
                "action": "search_tweets",
                "query": query,
                "error": str(e),
                "success": False,
            }
    
    async def _timeline_action(self, username: str) -> Dict[str, Any]:
        """Execute user timeline action."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.twitter_client.get_user_timeline, username, 10
            )
            return {
                "action": "get_timeline",
                "username": username,
                "result": result,
                "success": True,
            }
        except Exception as e:
            return {
                "action": "get_timeline",
                "username": username,
                "error": str(e),
                "success": False,
            }


class TwitterTaskAgent:
    """High-level agent for common Twitter tasks."""
    
    def __init__(self, react_agent: TwitterReACtAgent):
        """Initialize with ReAct agent."""
        self.react_agent = react_agent
    
    async def research_and_tweet(self, topic: str) -> Dict[str, Any]:
        """Research a topic and create a tweet about it."""
        task = f"Research the topic '{topic}' and create an informative tweet about it"
        
        # First, research the topic
        research_result = await self.react_agent.execute_task(f"Research: {topic}")
        
        if not research_result.get("success"):
            return research_result
        
        # Extract research content
        research_content = ""
        for result in research_result.get("results", []):
            if result.get("action") == "research" and result.get("success"):
                research_content = result.get("result", "")
                break
        
        if not research_content:
            return {
                "task": task,
                "error": "No research content found",
                "success": False,
            }
        
        # Generate tweet content based on research
        tweet_task = f"Create a tweet about '{topic}' using this research: {research_content[:500]}..."
        tweet_result = await self.react_agent.execute_task(tweet_task)
        
        return {
            "task": task,
            "research": research_content,
            "tweet_result": tweet_result,
            "success": tweet_result.get("success", False),
        }
    
    async def analyze_topic_sentiment(self, topic: str) -> Dict[str, Any]:
        """Analyze sentiment around a topic on Twitter."""
        task = f"Search for tweets about '{topic}' and analyze the sentiment"
        
        # Search for tweets
        search_result = await self.react_agent.execute_task(f"Search tweets: {topic}")
        
        if not search_result.get("success"):
            return search_result
        
        # Research the topic for context
        research_result = await self.react_agent.execute_task(f"Research sentiment analysis for: {topic}")
        
        return {
            "task": task,
            "search_result": search_result,
            "research_result": research_result,
            "success": True,
        }