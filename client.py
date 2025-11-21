"""
LangGraph Client for FastMCP Server
Connects to MCP server and uses LangGraph with OpenAI GPT-4o-mini
"""

import asyncio
import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()


class AgentState(TypedDict):
    """State of the agent conversation"""
    messages: Annotated[list[BaseMessage], add_messages]


def create_mcp_tool(tool_name: str, tool_description: str, session: ClientSession):
    """Create a LangChain tool from MCP tool"""
    async def tool_func(**kwargs):
        """Execute MCP tool"""
        try:
            result = await session.call_tool(tool_name, arguments=kwargs)
            if result.content:
                content = result.content[0]
                return content.text if hasattr(content, "text") else str(content)
            return str(result)
        except Exception as e:
            return f"Error calling tool: {str(e)}"
    
    return StructuredTool.from_function(
        coroutine=tool_func,
        name=tool_name,
        description=tool_description or f"Execute {tool_name}",
    )


def build_graph(llm, tools):
    """Build the LangGraph workflow"""
    async def call_model(state: AgentState) -> AgentState:
        """Call the LLM with the current state"""
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue or end"""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


async def run_query(graph, query: str):
    """Run a single query through the graph"""
    print(f"{'=' * 60}")
    print(f"💬 User: {query}")
    print(f"{'=' * 60}")

    initial_state = {"messages": [HumanMessage(content=query)]}

    async for event in graph.astream(initial_state, stream_mode="values"):
        messages = event.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        print(f"\n� Calling tool: {tool_call['name']}")
                        print(f"   Args: {tool_call['args']}")
                elif last_message.content:
                    print(f"\n🤖 Agent: {last_message.content}")

    print("\n")


async def main():
    """Main function to run the MCP LangGraph client"""
    SERVER_URL = "http://0.0.0.0:8002/sse"
    
    try:
        print("🔌 Connecting to MCP server...")
        
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                
                # Get available tools
                tools_response = await session.list_tools()
                print(f"✅ Connected! Found {len(tools_response.tools)} tools:")
                for tool in tools_response.tools:
                    print(f"  📦 {tool.name}: {tool.description}")
                
                # Create LangChain tools
                tools = [
                    create_mcp_tool(tool.name, tool.description, session)
                    for tool in tools_response.tools
                ]
                
                # Initialize LLM with tools
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=os.environ["OPENAI_API_KEY"],
                ).bind_tools(tools)
                
                # Build and compile graph
                graph = build_graph(llm, tools)
                print("✅ LangGraph compiled successfully\n")
                
                # Interactive mode
                print("=" * 60)
                print("🚀 MCP LangGraph Client")
                print("   Ask me anything about emails or Instagram profiles!")
                print("   Type 'quit' or 'exit' to stop.")
                print("=" * 60)
                
                while True:
                    try:
                        query = input("\n💭 Your query: ").strip()
                        
                        if not query:
                            continue
                        
                        if query.lower() in ["quit", "exit", "q"]:
                            print("👋 Goodbye!")
                            break
                        
                        await run_query(graph, query)
                        
                    except KeyboardInterrupt:
                        print("\n👋 Goodbye!")
                        break

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the client
    asyncio.run(main())
