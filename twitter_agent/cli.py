"""CLI interface for the Twitter Agent."""

import click
import asyncio
import logging
import json
from typing import Optional
from .config import load_config
from .twitter_client import TwitterClient
from .thesis_research import ThesisResearcher
from .agent import TwitterReACtAgent, TwitterTaskAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def main(ctx: click.Context, debug: bool) -> None:
    """Twitter Agent CLI - AI-powered Twitter automation with research capabilities."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    try:
        twitter_config, thesis_config, agent_config = load_config()
        ctx.ensure_object(dict)
        ctx.obj['twitter_config'] = twitter_config
        ctx.obj['thesis_config'] = thesis_config
        ctx.obj['agent_config'] = agent_config
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        ctx.exit(1)


@main.command()
@click.argument('topic')
@click.option('--post', is_flag=True, help='Actually post the tweet (default: dry run)')
@click.pass_context
def research_and_tweet(ctx: click.Context, topic: str, post: bool) -> None:
    """Research a topic and generate a tweet about it."""
    click.echo(f"🔍 Researching topic: {topic}")
    
    try:
        # Initialize components
        twitter_client = TwitterClient(ctx.obj['twitter_config'])
        thesis_researcher = ThesisResearcher(ctx.obj['thesis_config'])
        react_agent = TwitterReACtAgent(twitter_client, thesis_researcher, ctx.obj['agent_config'])
        task_agent = TwitterTaskAgent(react_agent)
        
        # Execute the task
        result = asyncio.run(task_agent.research_and_tweet(topic))
        
        if result.get('success'):
            click.echo("✅ Task completed successfully!")
            
            # Display research summary
            research_content = result.get('research', '')
            if research_content:
                click.echo(f"\n📚 Research Summary:")
                click.echo(research_content[:300] + "..." if len(research_content) > 300 else research_content)
            
            # Display tweet result
            tweet_result = result.get('tweet_result', {})
            if tweet_result.get('results'):
                for tweet_action in tweet_result['results']:
                    if tweet_action.get('action') == 'tweet':
                        tweet_content = tweet_action.get('content', '')
                        click.echo(f"\n🐦 Generated Tweet:")
                        click.echo(f"'{tweet_content}'")
                        
                        if post:
                            if tweet_action.get('success'):
                                tweet_id = tweet_action.get('result', {}).get('tweet_id')
                                click.echo(f"✅ Tweet posted successfully! ID: {tweet_id}")
                            else:
                                error = tweet_action.get('error', 'Unknown error')
                                click.echo(f"❌ Failed to post tweet: {error}")
                        else:
                            click.echo("(Dry run - use --post to actually tweet)")
        else:
            error = result.get('error', 'Unknown error')
            click.echo(f"❌ Task failed: {error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.argument('query')
@click.pass_context
def research(ctx: click.Context, query: str) -> None:
    """Research a query using Thesis API."""
    click.echo(f"🔍 Researching: {query}")
    
    try:
        thesis_researcher = ThesisResearcher(ctx.obj['thesis_config'])
        result = asyncio.run(thesis_researcher.research_query(query))
        
        click.echo("✅ Research completed!")
        click.echo(f"\n📚 Results:")
        click.echo(result)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.argument('text')
@click.pass_context
def tweet(ctx: click.Context, text: str) -> None:
    """Post a tweet."""
    if len(text) > 280:
        click.echo("⚠️  Tweet is longer than 280 characters, it will be truncated.")
    
    click.echo(f"🐦 Posting tweet: '{text}'")
    
    try:
        twitter_client = TwitterClient(ctx.obj['twitter_config'])
        result = twitter_client.post_tweet(text)
        
        if result.get('success'):
            tweet_id = result.get('tweet_id')
            click.echo(f"✅ Tweet posted successfully! ID: {tweet_id}")
        else:
            error = result.get('error', 'Unknown error')
            click.echo(f"❌ Failed to post tweet: {error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.argument('query')
@click.option('--count', default=10, help='Number of tweets to search')
@click.pass_context
def search(ctx: click.Context, query: str, count: int) -> None:
    """Search for tweets."""
    click.echo(f"🔍 Searching tweets for: {query}")
    
    try:
        twitter_client = TwitterClient(ctx.obj['twitter_config'])
        tweets = twitter_client.search_tweets(query, count)
        
        if tweets:
            click.echo(f"✅ Found {len(tweets)} tweets:")
            for i, tweet in enumerate(tweets, 1):
                click.echo(f"\n{i}. @{tweet.get('author_screen_name', tweet.get('author_id', 'unknown'))}")
                click.echo(f"   {tweet['text']}")
                click.echo(f"   Created: {tweet['created_at']}")
                metrics = tweet.get('metrics', {})
                if metrics:
                    click.echo(f"   Metrics: {metrics}")
        else:
            click.echo("❌ No tweets found.")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.argument('username')
@click.option('--count', default=10, help='Number of tweets to retrieve')
@click.pass_context
def timeline(ctx: click.Context, username: str, count: int) -> None:
    """Get user timeline."""
    click.echo(f"📱 Getting timeline for: @{username}")
    
    try:
        twitter_client = TwitterClient(ctx.obj['twitter_config'])
        tweets = twitter_client.get_user_timeline(username, count)
        
        if tweets:
            click.echo(f"✅ Found {len(tweets)} tweets:")
            for i, tweet in enumerate(tweets, 1):
                click.echo(f"\n{i}. {tweet['text']}")
                click.echo(f"   Created: {tweet['created_at']}")
                metrics = tweet.get('metrics', {})
                if metrics:
                    click.echo(f"   Metrics: {metrics}")
        else:
            click.echo("❌ No tweets found.")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.argument('task')
@click.pass_context
def agent(ctx: click.Context, task: str) -> None:
    """Execute a custom task using the ReAct agent."""
    click.echo(f"🤖 Executing task: {task}")
    
    try:
        twitter_client = TwitterClient(ctx.obj['twitter_config'])
        thesis_researcher = ThesisResearcher(ctx.obj['thesis_config'])
        react_agent = TwitterReACtAgent(twitter_client, thesis_researcher, ctx.obj['agent_config'])
        
        result = asyncio.run(react_agent.execute_task(task))
        
        if result.get('success'):
            click.echo("✅ Task completed successfully!")
            
            reasoning = result.get('reasoning', '')
            if reasoning:
                click.echo(f"\n🧠 Reasoning:")
                click.echo(reasoning)
            
            actions = result.get('actions', [])
            if actions:
                click.echo(f"\n⚡ Actions taken:")
                for i, action in enumerate(actions, 1):
                    click.echo(f"  {i}. {action['action']}: {action['input']}")
            
            results = result.get('results', [])
            if results:
                click.echo(f"\n📊 Results:")
                for i, res in enumerate(results, 1):
                    success_indicator = "✅" if res.get('success') else "❌"
                    click.echo(f"  {i}. {success_indicator} {res.get('action', 'Unknown')}")
                    if res.get('result'):
                        # Truncate long results
                        result_text = str(res['result'])
                        if len(result_text) > 200:
                            result_text = result_text[:200] + "..."
                        click.echo(f"     Result: {result_text}")
                    if res.get('error'):
                        click.echo(f"     Error: {res['error']}")
            
            final_answer = result.get('final_answer', '')
            if final_answer:
                click.echo(f"\n🎯 Final Answer:")
                click.echo(final_answer)
                
        else:
            error = result.get('error', 'Unknown error')
            click.echo(f"❌ Task failed: {error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@main.command()
@click.pass_context
def config_check(ctx: click.Context) -> None:
    """Check configuration status."""
    click.echo("🔧 Configuration Status:")
    
    twitter_config = ctx.obj['twitter_config']
    thesis_config = ctx.obj['thesis_config']
    agent_config = ctx.obj['agent_config']
    
    # Check Twitter configuration
    click.echo("\n🐦 Twitter Configuration:")
    click.echo(f"  API Key: {'✅ Set' if twitter_config.api_key else '❌ Missing'}")
    click.echo(f"  API Secret: {'✅ Set' if twitter_config.api_secret else '❌ Missing'}")
    click.echo(f"  Access Token: {'✅ Set' if twitter_config.access_token else '❌ Missing'}")
    click.echo(f"  Access Token Secret: {'✅ Set' if twitter_config.access_token_secret else '❌ Missing'}")
    click.echo(f"  Bearer Token: {'✅ Set' if twitter_config.bearer_token else '⚠️  Optional'}")
    
    # Check Thesis configuration
    click.echo("\n📚 Thesis Configuration:")
    click.echo(f"  Auth Token: {'✅ Set' if thesis_config.auth_token else '❌ Missing'}")
    click.echo(f"  Device ID: {'✅ Set' if thesis_config.device_id else '❌ Missing'}")
    click.echo(f"  Space ID: {thesis_config.space_id}")
    
    # Check Agent configuration
    click.echo("\n🤖 Agent Configuration:")
    click.echo(f"  OpenAI API Key: {'✅ Set' if agent_config.openai_api_key else '⚠️  Optional'}")
    click.echo(f"  Model: {agent_config.model}")
    click.echo(f"  Max Tokens: {agent_config.max_tokens}")
    click.echo(f"  Temperature: {agent_config.temperature}")


if __name__ == '__main__':
    main()