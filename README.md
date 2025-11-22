# MCP Tool Client and Server

A simplified Model Context Protocol (MCP) implementation with LangGraph integration and OpenAI GPT-4o-mini.

## Project Structure

```
.
├── fastmcp_http_server.py  # MCP server with Twitter tools (port 8002)
├── slack_mcp_server.py     # MCP server with Slack tools (port 8003)
├── client.py               # LangGraph client with OpenAI integration
├── mcp_client.py          # Simple MCP client with interactive mode
└── .env                   # Environment variables (not tracked)
```

## Setup

1. **Install dependencies:**
```bash
pip install fastmcp langchain-openai langgraph python-dotenv openai mcp
```

2. **Configure environment variables:**
Create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### 1. Start the MCP Servers

**Twitter MCP Server:**
```bash
python3 fastmcp_http_server.py
```
Server will run on `http://0.0.0.0:8002/sse`

**Slack MCP Server:**
```bash
python3 slack_mcp_server.py
```
Server will run on `http://0.0.0.0:8003/sse`

### 2. Run the LangGraph Client
```bash
python3 client.py
```
Executes predefined queries using LangGraph workflow.

### 3. Run the Interactive MCP Client
```bash
python3 mcp_client.py
```
Interactive mode - ask questions in natural language.

Or single query mode:
```bash
python3 mcp_client.py "Get my latest emails"
```

## Available Tools

### Twitter MCP Server (Port 8002)
- **send_tweet**: Send a tweet
  - Parameters: `text`
  
- **get_comments**: Get comments/replies on a tweet
  - Parameters: `tweet_id`, `max_results`
  
- **get_profile_data**: Get Twitter profile data
  
- **get_posts**: Get recent tweets/posts from timeline
  - Parameters: `max_results`

### Slack MCP Server (Port 8003)
- **send_message**: Send a message to a Slack channel
  - Parameters: `channel`, `text`, `thread_ts` (optional)
  
- **get_channel_messages**: Get recent messages from a channel
  - Parameters: `channel`, `limit`
  
- **get_thread_replies**: Get replies to a thread
  - Parameters: `channel`, `thread_ts`, `limit`
  
- **list_channels**: List all available Slack channels
  
- **get_user_profile**: Get Slack user profile information
  - Parameters: `user_id` (optional)
  
- **search_messages**: Search for messages across channels
  - Parameters: `query`, `count`
  
- **add_reaction**: Add a reaction emoji to a message
  - Parameters: `channel`, `timestamp`, `reaction`
  
- **get_workspace_info**: Get information about the Slack workspace

## Architecture

- **Server**: FastMCP HTTP server with SSE transport
- **Client**: LangGraph workflow with OpenAI GPT-4o-mini
- **Tools**: Automatically converted from MCP to LangChain format
