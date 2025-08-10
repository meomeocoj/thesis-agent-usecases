"""Twitter API integration using tweepy."""

import tweepy
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter API client wrapper."""
    
    def __init__(self, config):
        """Initialize Twitter client with configuration."""
        self.config = config
        
        # Initialize API v1.1 for posting tweets
        auth = tweepy.OAuthHandler(config.api_key, config.api_secret)
        auth.set_access_token(config.access_token, config.access_token_secret)
        self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Initialize API v2 for advanced features
        if config.bearer_token:
            self.client_v2 = tweepy.Client(
                bearer_token=config.bearer_token,
                consumer_key=config.api_key,
                consumer_secret=config.api_secret,
                access_token=config.access_token,
                access_token_secret=config.access_token_secret,
                wait_on_rate_limit=True,
            )
        else:
            self.client_v2 = None
            logger.warning("Bearer token not provided, some v2 features unavailable")
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """Post a tweet."""
        try:
            if len(text) > 280:
                text = text[:277] + "..."
            
            if self.client_v2:
                response = self.client_v2.create_tweet(text=text)
                return {
                    "success": True,
                    "tweet_id": response.data["id"],
                    "text": text,
                }
            else:
                tweet = self.api_v1.update_status(text)
                return {
                    "success": True,
                    "tweet_id": tweet.id_str,
                    "text": text,
                }
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text,
            }
    
    def search_tweets(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """Search for tweets."""
        try:
            if self.client_v2:
                tweets = self.client_v2.search_recent_tweets(
                    query=query,
                    max_results=min(count, 100),
                    tweet_fields=["author_id", "created_at", "public_metrics"],
                )
                
                if not tweets.data:
                    return []
                
                return [
                    {
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "metrics": tweet.public_metrics,
                    }
                    for tweet in tweets.data
                ]
            else:
                tweets = tweepy.Cursor(
                    self.api_v1.search_tweets,
                    q=query,
                    result_type="recent",
                    lang="en",
                ).items(count)
                
                return [
                    {
                        "id": tweet.id_str,
                        "text": tweet.text,
                        "author_id": tweet.user.id_str,
                        "author_screen_name": tweet.user.screen_name,
                        "created_at": tweet.created_at.isoformat(),
                        "metrics": {
                            "retweet_count": tweet.retweet_count,
                            "favorite_count": tweet.favorite_count,
                        },
                    }
                    for tweet in tweets
                ]
                
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    def get_user_timeline(self, username: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user timeline."""
        try:
            if self.client_v2:
                user = self.client_v2.get_user(username=username)
                if not user.data:
                    return []
                
                tweets = self.client_v2.get_users_tweets(
                    user.data.id,
                    max_results=min(count, 100),
                    tweet_fields=["created_at", "public_metrics"],
                )
                
                if not tweets.data:
                    return []
                
                return [
                    {
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "metrics": tweet.public_metrics,
                    }
                    for tweet in tweets.data
                ]
            else:
                tweets = tweepy.Cursor(
                    self.api_v1.user_timeline,
                    screen_name=username,
                    exclude_replies=True,
                    include_rts=False,
                ).items(count)
                
                return [
                    {
                        "id": tweet.id_str,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat(),
                        "metrics": {
                            "retweet_count": tweet.retweet_count,
                            "favorite_count": tweet.favorite_count,
                        },
                    }
                    for tweet in tweets
                ]
                
        except Exception as e:
            logger.error(f"Error getting user timeline: {e}")
            return []