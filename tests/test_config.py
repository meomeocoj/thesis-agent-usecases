"""Tests for configuration module."""

import os
import pytest
from twitter_agent.config import TwitterConfig, ThesisConfig, AgentConfig, load_config


def test_twitter_config():
    """Test TwitterConfig model."""
    config = TwitterConfig(
        api_key="test_key",
        api_secret="test_secret", 
        access_token="test_token",
        access_token_secret="test_token_secret"
    )
    
    assert config.api_key == "test_key"
    assert config.api_secret == "test_secret"
    assert config.access_token == "test_token"
    assert config.access_token_secret == "test_token_secret"
    assert config.bearer_token is None


def test_thesis_config():
    """Test ThesisConfig model."""
    config = ThesisConfig(auth_token="test_token", device_id="test_device")
    
    assert config.auth_token == "test_token"
    assert config.device_id == "test_device"
    assert config.space_id == "402"


def test_agent_config():
    """Test AgentConfig model."""
    config = AgentConfig()
    
    assert config.model == "gpt-3.5-turbo"
    assert config.max_tokens == 1000
    assert config.temperature == 0.7


def test_load_config_with_env_vars(monkeypatch):
    """Test loading configuration with environment variables."""
    # Set environment variables
    monkeypatch.setenv("TWITTER_API_KEY", "env_api_key")
    monkeypatch.setenv("TWITTER_API_SECRET", "env_api_secret")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "env_access_token")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET", "env_access_token_secret")
    monkeypatch.setenv("THESIS_AUTH_TOKEN", "env_thesis_token")
    monkeypatch.setenv("OPENAI_API_KEY", "env_openai_key")
    
    twitter_config, thesis_config, agent_config = load_config()
    
    assert twitter_config.api_key == "env_api_key"
    assert twitter_config.api_secret == "env_api_secret"
    assert twitter_config.access_token == "env_access_token"
    assert twitter_config.access_token_secret == "env_access_token_secret"
    
    assert thesis_config.auth_token == "env_thesis_token"
    assert thesis_config.device_id == "5e73524bfcb95a64886ded5c99f0776f"  # default
    
    assert agent_config.openai_api_key == "env_openai_key"