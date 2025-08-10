#!/usr/bin/env python3
"""
Twitter Agent - Main entry point

A sophisticated AI-powered Twitter agent that combines DSpy's ReAct framework 
with the Thesis conversation API for intelligent research and Twitter automation.

This is the main entry point that can be used as an alternative to the CLI.
For full CLI functionality, use: tweet-agent command
"""

import asyncio
import logging
from twitter_agent.config import load_config
from twitter_agent.twitter_client import TwitterClient
from twitter_agent.thesis_research import ThesisResearcher
from twitter_agent.agent import TwitterReACtAgent, TwitterTaskAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating the Twitter Agent capabilities."""
    print("=& Twitter Agent - DSpy ReAct with Thesis API Integration")
    print("=" * 60)
    
    try:
        # Load configuration
        print("=Ë Loading configuration...")
        twitter_config, thesis_config, agent_config = load_config()
        
        # Initialize components
        print("=' Initializing components...")
        twitter_client = TwitterClient(twitter_config)
        thesis_researcher = ThesisResearcher(thesis_config)
        react_agent = TwitterReACtAgent(twitter_client, thesis_researcher, agent_config)
        task_agent = TwitterTaskAgent(react_agent)
        
        # Example usage - Research and tweet about a topic
        topic = "artificial intelligence trends 2024"
        print(f"\n= Example: Researching and tweeting about '{topic}'")
        
        result = await task_agent.research_and_tweet(topic)
        
        if result.get('success'):
            print(" Task completed successfully!")
            
            # Display research summary
            research_content = result.get('research', '')
            if research_content:
                print(f"\n=Ú Research Summary:")
                print(research_content[:300] + "..." if len(research_content) > 300 else research_content)
            
            # Display tweet result
            tweet_result = result.get('tweet_result', {})
            if tweet_result.get('results'):
                for tweet_action in tweet_result['results']:
                    if tweet_action.get('action') == 'tweet':
                        tweet_content = tweet_action.get('content', '')
                        print(f"\n=& Generated Tweet:")
                        print(f"'{tweet_content}'")
                        print("(Note: This is a dry run - use CLI with --post to actually tweet)")
        else:
            error = result.get('error', 'Unknown error')
            print(f"L Task failed: {error}")
        
        print(f"\n=¡ For full functionality, use the CLI:")
        print(f"   tweet-agent research-and-tweet '{topic}' --post")
        print(f"   tweet-agent config-check")
        print(f"   tweet-agent --help")
        
    except Exception as e:
        print(f"L Error: {e}")
        print("\n=' Check your configuration:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your API keys and tokens")
        print("   3. Run: tweet-agent config-check")


if __name__ == "__main__":
    asyncio.run(main())