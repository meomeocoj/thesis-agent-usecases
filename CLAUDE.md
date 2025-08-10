# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python research project exploring AI agent use cases, specifically focused on conversation creation through the Thesis.io platform. The project contains utilities for creating conversations via API calls to staging/beta environments.

## Development Setup

**Python Version:** Requires Python 3.12+

**Install Dependencies:**
```bash
pip install -e ".[dev]"
```

**Development Tools:**
- `black` - Code formatting
- `isort` - Import sorting  
- `flake8` - Linting
- `mypy` - Type checking
- `pytest` - Testing

## Key Commands

**Formatting:**
```bash
black .
isort .
```

**Linting:**
```bash
flake8
mypy .
```

**Testing:**
```bash
pytest
pytest tests/test_specific.py  # Run specific test file
pytest -v  # Verbose output
pytest --cov  # With coverage
```

## Architecture

The project consists of two main modules:

**`create_conversation.py`** - Core API client for the Thesis.io conversation API
- `create_conversation()` - Creates individual conversations
- `create_batch_conversation()` - Handles multiple conversation creation
- Uses aiohttp for async HTTP requests
- Configured for staging auth (auth-staging.thesis.io) and beta backend (backend-beta.thesis.io)

**`twitter-agent.py`** - Agent specification (currently minimal implementation)

**API Configuration:**
- Space ID: 402 (hardcoded for current use case)
- Authentication via JWT bearer tokens (hardcoded in headers)
- Device ID tracking for API calls

## Important Notes

- The project contains hardcoded JWT tokens and device IDs in `create_conversation.py` - these are for development/staging use
- API endpoints point to staging/beta environments
- The codebase follows Python 3.12+ conventions with full type hints required (mypy strict mode)