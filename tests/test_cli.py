"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from twitter_agent.cli import main


def test_cli_main_help():
    """Test CLI main command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    
    assert result.exit_code == 0
    assert 'Twitter Agent CLI' in result.output
    assert 'research-and-tweet' in result.output
    assert 'research' in result.output
    assert 'tweet' in result.output


def test_cli_config_check():
    """Test config-check command."""
    runner = CliRunner()
    result = runner.invoke(main, ['config-check'])
    
    # Should run but may show missing config warnings
    assert 'Configuration Status' in result.output
    assert 'Twitter Configuration' in result.output
    assert 'Thesis Configuration' in result.output


def test_cli_research_help():
    """Test research command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['research', '--help'])
    
    assert result.exit_code == 0
    assert 'Research a query using Thesis API' in result.output


def test_cli_tweet_help():
    """Test tweet command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['tweet', '--help'])
    
    assert result.exit_code == 0
    assert 'Post a tweet' in result.output


def test_cli_search_help():
    """Test search command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['search', '--help'])
    
    assert result.exit_code == 0
    assert 'Search for tweets' in result.output
    assert '--count' in result.output


def test_cli_timeline_help():
    """Test timeline command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['timeline', '--help'])
    
    assert result.exit_code == 0
    assert 'Get user timeline' in result.output
    assert '--count' in result.output


def test_cli_agent_help():
    """Test agent command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['agent', '--help'])
    
    assert result.exit_code == 0
    assert 'Execute a custom task using the ReAct agent' in result.output


def test_cli_research_and_tweet_help():
    """Test research-and-tweet command help."""
    runner = CliRunner()
    result = runner.invoke(main, ['research-and-tweet', '--help'])
    
    assert result.exit_code == 0
    assert 'Research a topic and generate a tweet' in result.output
    assert '--post' in result.output