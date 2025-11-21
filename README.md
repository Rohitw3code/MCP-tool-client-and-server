# MCP Tool Client and Server

A simplified Model Context Protocol (MCP) implementation with LangGraph integration and OpenAI GPT-4o-mini.

## Project Structure

```
.
├── fastmcp_http_server.py  # MCP server with Gmail & Instagram tools
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

### 1. Start the MCP Server
```bash
python3 fastmcp_http_server.py
```
Server will run on `http://0.0.0.0:8002/sse`

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

- **get_gmail_emails**: Retrieve emails from Gmail
  - Parameters: `max_results`, `query`, `label`
  
- **get_instagram_profile**: Get Instagram profile info
  - Parameters: `username`

## Architecture

- **Server**: FastMCP HTTP server with SSE transport
- **Client**: LangGraph workflow with OpenAI GPT-4o-mini
- **Tools**: Automatically converted from MCP to LangChain format
