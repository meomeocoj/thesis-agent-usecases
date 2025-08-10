"""Configuration management for Twitter Agent."""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class TwitterConfig(BaseModel):
    """Twitter API configuration."""
    
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: Optional[str] = None


class ThesisConfig(BaseModel):
    """Thesis API configuration."""
    
    base_url_auth: str = "https://auth-staging.thesis.io/api"
    base_url_backend: str = "https://backend-beta.thesis.io/api"
    space_id: str = "402"
    auth_token: str
    device_id: str


class AgentConfig(BaseModel):
    """Agent configuration."""
    
    openai_api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7


def load_config() -> tuple[TwitterConfig, ThesisConfig, AgentConfig]:
    """Load configuration from environment variables."""
    
    twitter_config = TwitterConfig(
        api_key=os.getenv("TWITTER_API_KEY", ""),
        api_secret=os.getenv("TWITTER_API_SECRET", ""),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    )
    
    thesis_config = ThesisConfig(
        auth_token=os.getenv("THESIS_AUTH_TOKEN", ""),
        device_id=os.getenv("THESIS_DEVICE_ID", "5e73524bfcb95a64886ded5c99f0776f"),
    )
    
    agent_config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("AGENT_MODEL", "gpt-3.5-turbo"),
        max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "1000")),
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
    )
    
    return twitter_config, thesis_config, agent_config