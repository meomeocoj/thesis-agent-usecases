# Twitter Agent with DSpy ReAct and Thesis API

A sophisticated AI-powered Twitter agent that combines DSpy's ReAct (Reasoning + Acting) framework with the Thesis conversation API for intelligent research and Twitter automation.

## Features

- 🤖 **DSpy ReAct Agent**: Intelligent reasoning and action planning for Twitter tasks
- 📚 **Thesis API Integration**: Deep research capabilities using conversation API
- 🐦 **Twitter SDK Integration**: Full Twitter API v1.1 and v2 support
- 💻 **CLI Interface**: Easy-to-use command-line interface
- 🔍 **Research & Tweet**: Automatically research topics and generate informative tweets
- 📊 **Sentiment Analysis**: Analyze Twitter sentiment on any topic
- 🔧 **Configurable**: Flexible configuration through environment variables

## Installation

1. Clone the repository:
```bash
git clone https://github.com/meomeocoj/thesis-agent-usecases.git
cd thesis-agent-usecases
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and tokens
```

## Configuration

### Required Environment Variables

#### Twitter API
- `TWITTER_API_KEY`: Your Twitter API key
- `TWITTER_API_SECRET`: Your Twitter API secret
- `TWITTER_ACCESS_TOKEN`: Your Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET`: Your Twitter access token secret
- `TWITTER_BEARER_TOKEN`: Your Twitter bearer token (optional, for v2 features)

#### Thesis API
- `THESIS_AUTH_TOKEN`: Your Thesis authentication token
- `THESIS_DEVICE_ID`: Your Thesis device ID (optional, defaults provided)

#### Agent Configuration (Optional)
- `OPENAI_API_KEY`: OpenAI API key for enhanced AI capabilities
- `AGENT_MODEL`: AI model to use (default: gpt-3.5-turbo)
- `AGENT_MAX_TOKENS`: Maximum tokens for AI responses (default: 1000)
- `AGENT_TEMPERATURE`: AI creativity level (default: 0.7)

## Usage

### CLI Commands

Check your configuration:
```bash
tweet-agent config-check
```

Research a topic using Thesis API:
```bash
tweet-agent research "artificial intelligence trends 2024"
```

Post a simple tweet:
```bash
tweet-agent tweet "Hello, world! 🌍"
```

Research and generate a tweet (dry run):
```bash
tweet-agent research-and-tweet "blockchain technology"
```

Research and actually post a tweet:
```bash
tweet-agent research-and-tweet "machine learning" --post
```

Search for tweets:
```bash
tweet-agent search "python programming" --count 5
```

Get user timeline:
```bash
tweet-agent timeline elonmusk --count 10
```

Execute custom agent tasks:
```bash
tweet-agent agent "Find trending topics in AI and suggest 3 tweet ideas"
```

### Advanced Usage

The ReAct agent can handle complex, multi-step tasks:

```bash
# Complex research and analysis
tweet-agent agent "Research the latest developments in quantum computing, find related tweets, and create a comprehensive summary"

# Sentiment analysis
tweet-agent agent "Search for tweets about climate change, analyze the sentiment, and provide insights"

# Content strategy
tweet-agent agent "Research trending topics in technology and suggest a content strategy for the next week"
```

## Architecture

### Components

1. **TwitterReACtAgent**: Core ReAct agent using DSpy framework
2. **ThesisResearcher**: Research capabilities using Thesis conversation API  
3. **TwitterClient**: Twitter API wrapper supporting both v1.1 and v2
4. **CLI**: Command-line interface for easy interaction
5. **Configuration**: Flexible configuration management

### ReAct Methodology

The agent uses the ReAct (Reasoning + Acting) approach:

1. **Think**: Analyze the task and plan actions
2. **Act**: Execute planned actions (research, tweet, search)
3. **Observe**: Process results and adapt if needed
4. **Repeat**: Continue until task completion

### Data Flow

```
User Input → ReAct Agent → Action Planning → Execution:
                                          ├── Thesis Research
                                          ├── Twitter Actions  
                                          └── Result Processing → User Output
```

## Examples

### Research and Tweet Workflow

```bash
# The agent will:
# 1. Research the topic using Thesis API
# 2. Analyze the research results
# 3. Generate an informative tweet
# 4. Post the tweet (if --post flag is used)

tweet-agent research-and-tweet "sustainable energy solutions" --post
```

### Custom Agent Tasks

```bash
# Multi-step analysis task
tweet-agent agent "Research recent AI breakthroughs, find tweets discussing them, and create a summary report with key insights and trending hashtags"
```

## Development

### Project Structure

```
twitter_agent/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── agent.py             # DSpy ReAct agent implementation
├── thesis_research.py   # Thesis API integration
├── twitter_client.py    # Twitter API wrapper
└── cli.py              # Command-line interface
```

### Adding New Actions

To add new actions to the ReAct agent:

1. Add action type to `_execute_action()` method in `agent.py`
2. Implement the action method (e.g., `_new_action()`)
3. Update CLI if needed for direct access

### Testing

Run the configuration check to ensure everything is set up correctly:

```bash
tweet-agent config-check
```

Test research functionality:
```bash
tweet-agent research "test query"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your API keys and tokens in `.env`
2. **Rate Limiting**: The agent handles rate limits automatically
3. **Connection Issues**: Check internet connectivity and API service status

### Debug Mode

Enable debug logging for troubleshooting:
```bash
tweet-agent --debug research-and-tweet "test topic"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [DSpy](https://github.com/stanfordnlp/dspy) - Framework for programming with foundation models
- [Tweepy](https://www.tweepy.org/) - Twitter API library
- [Thesis](https://thesis.io/) - Conversation and research API
- [Click](https://click.palletsprojects.com/) - Command-line interface framework