import asyncio
import json
import os
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
SERVER_URL = "http://0.0.0.0:8002/sse"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)


async def get_available_tools(session: ClientSession) -> list[dict]:
    """Fetch available tools from the MCP server and format them for OpenAI."""
    tools_response = await session.list_tools()
    
    openai_tools = []
    for tool in tools_response.tools:
        # Convert MCP tool schema to OpenAI tool format
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        }
        openai_tools.append(openai_tool)
    
    return openai_tools


def ask_ai_for_tool_call(query: str, available_tools: list[dict]) -> dict | None:
    """
    Ask GPT-4o-mini to decide which tool to call based on the user's query.
    
    Args:
        query: User's natural language query
        available_tools: List of available tools in OpenAI tool format
    
    Returns:
        Dictionary with tool_name and arguments, or None if no tool needed
    """
    system_prompt = """You are an AI assistant that helps users interact with Gmail and Instagram tools.
Based on the user's query, decide which tool to call and with what arguments.

Available tools:
1. get_gmail_emails - Retrieves emails from Gmail. Parameters:
   - max_results (int): Maximum emails to retrieve (default: 10)
   - query (str, optional): Search query to filter emails
   - label (str, optional): Gmail label (default: INBOX)

2. get_instagram_profile - Gets Instagram profile info. Parameters:
   - username (str, required): Instagram username to look up

If the user's query doesn't relate to these tools, respond normally without using tools.
Always extract relevant parameters from the user's query."""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        tools=available_tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # Check if GPT decided to use a tool
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        return {
            "tool_name": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments),
            "tool_call_id": tool_call.id
        }
    
    # No tool was called - return the text response
    if message.content:
        return {
            "tool_name": None,
            "text_response": message.content
        }
    
    return None


async def execute_tool(session: ClientSession, tool_name: str, arguments: dict) -> str:
    """Execute a tool on the MCP server and return the result."""
    result = await session.call_tool(tool_name, arguments)
    
    for content in result.content:
        if content.type == "text":
            return content.text
    
    return json.dumps({"error": "No result returned"})


def format_response_with_ai(query: str, tool_name: str, tool_result: str) -> str:
    """Use GPT-4o-mini to format the tool result into a natural language response."""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""The user asked: "{query}"

I called the tool '{tool_name}' and got this result:
{tool_result}

Please provide a helpful, well-formatted response to the user based on this data. 
Use emojis where appropriate and format the information clearly."""
            }
        ]
    )
    
    return response.choices[0].message.content


async def process_query(query: str):
    """
    Process a user query using AI to decide tool calls.
    
    Args:
        query: Natural language query from the user
    """
    print(f"\n🔍 Processing: {query}")
    print("-" * 50)
    
    async with sse_client(SERVER_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the MCP connection
            await session.initialize()
            
            # Get available tools from MCP server
            available_tools = await get_available_tools(session)
            print(f"📦 Found {len(available_tools)} available tools")
            
            # Ask GPT-4o-mini which tool to call
            print("🤖 Asking AI to analyze query...")
            tool_decision = ask_ai_for_tool_call(query, available_tools)
            
            if tool_decision is None:
                print("❌ Could not process the query")
                return
            
            # If no tool was needed, return Claude's direct response
            if tool_decision.get("tool_name") is None:
                print("\n💬 AI Response:")
                print(tool_decision.get("text_response", "No response"))
                return
            
            tool_name = tool_decision["tool_name"]
            arguments = tool_decision["arguments"]
            
            print(f"🔧 AI decided to call: {tool_name}")
            print(f"   Arguments: {json.dumps(arguments, indent=2)}")
            
            # Execute the tool on MCP server
            print("\n⏳ Executing tool...")
            tool_result = await execute_tool(session, tool_name, arguments)
            
            # Format the response using GPT-4o-mini
            print("✨ Formatting response...\n")
            formatted_response = format_response_with_ai(query, tool_name, tool_result)
            
            print("=" * 50)
            print("📋 RESULT:")
            print("=" * 50)
            print(formatted_response)


async def interactive_mode():
    """Run the client in interactive mode."""
    print("=" * 60)
    print("🚀 AI-Powered MCP Client")
    print("   Gmail & Instagram Tools with GPT-4o-mini")
    print("=" * 60)
    print("\nAsk me anything about emails or Instagram profiles!")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            query = input("\n💭 Your query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            await process_query(query)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main entry point."""
    import sys
    
    # Check for API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        await process_query(query)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())