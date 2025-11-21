"""
LangGraph Client for FastMCP Server
Uses mcp-adapter to connect to the HTTP MCP server
"""

import asyncio
import os
from typing import Annotated, Literal, TypedDict

import httpx
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()


# Define the state for our graph
class AgentState(TypedDict):
    """State of the agent conversation"""

    messages: Annotated[list[BaseMessage], add_messages]


class MCPLangGraphClient:
    """LangGraph client that connects to MCP server"""

    def __init__(self, mcp_server_url: str = "http://0.0.0.0:8002/sse"):
        self.mcp_server_url = mcp_server_url
        self.session = None
        self.tools = []
        self.llm = None
        self.graph = None

    async def initialize(self):
        """Initialize the MCP connection and LangGraph"""
        print("🔌 Connecting to MCP server...")

        # Connect to MCP server via SSE
        async with httpx.AsyncClient() as client:
            async with sse_client(self.mcp_server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session

                    # Initialize the session
                    await session.initialize()

                    # List available tools from MCP server
                    tools_response = await session.list_tools()
                    print(f"✅ Connected! Found {len(tools_response.tools)} tools")

                    # Convert MCP tools to LangChain tools
                    self.tools = await self._convert_mcp_tools_to_langchain(
                        session, tools_response.tools
                    )

                    # Initialize LLM with tools
                    self.llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0,
                        api_key=os.environ["OPENAI_API_KEY"],
                    ).bind_tools(self.tools)

                    # Build the LangGraph
                    self._build_graph()

                    return session

    async def _convert_mcp_tools_to_langchain(self, session, mcp_tools):
        """Convert MCP tools to LangChain compatible tools"""
        from langchain_core.tools import StructuredTool

        langchain_tools = []

        for mcp_tool in mcp_tools:
            # Create a closure to capture the tool name and session
            def make_tool_func(tool_name, mcp_session):
                async def tool_func(**kwargs):
                    """Execute MCP tool"""
                    try:
                        result = await mcp_session.call_tool(
                            tool_name, arguments=kwargs
                        )
                        # Extract content from result
                        if result.content:
                            content = result.content[0]
                            return (
                                content.text
                                if hasattr(content, "text")
                                else str(content)
                            )
                        return str(result)
                    except Exception as e:
                        return f"Error calling tool: {str(e)}"

                return tool_func

            # Create LangChain tool using StructuredTool
            tool = StructuredTool.from_function(
                coroutine=make_tool_func(mcp_tool.name, session),
                name=mcp_tool.name,
                description=mcp_tool.description or f"Execute {mcp_tool.name}",
            )

            langchain_tools.append(tool)
            print(f"  📦 Loaded tool: {mcp_tool.name}")

        return langchain_tools

    def _build_graph(self):
        """Build the LangGraph workflow"""

        # Define the agent node
        async def call_model(state: AgentState) -> AgentState:
            """Call the LLM with the current state"""
            messages = state["messages"]
            response = await self.llm.ainvoke(messages)
            return {"messages": [response]}

        # Define routing function
        def should_continue(state: AgentState) -> Literal["tools", "end"]:
            """Determine if we should continue or end"""
            messages = state["messages"]
            last_message = messages[-1]

            # If there are tool calls, continue to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"

            # Otherwise, end
            return "end"

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent", should_continue, {"tools": "tools", "end": END}
        )
        workflow.add_edge("tools", "agent")

        # Compile the graph
        self.graph = workflow.compile()
        print("✅ LangGraph compiled successfully")

    async def run(self, user_message: str) -> str:
        """Run the agent with a user message"""
        if not self.graph:
            raise ValueError("Graph not initialized. Call initialize() first.")

        print(f"\n💬 User: {user_message}")
        print("🤔 Agent is thinking...\n")

        # Create initial state
        initial_state = {"messages": [HumanMessage(content=user_message)]}

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Extract the final response
        final_message = final_state["messages"][-1]

        if isinstance(final_message, AIMessage):
            response = final_message.content
            print(f"🤖 Agent: {response}\n")
            return response

        return str(final_message)

    async def stream_run(self, user_message: str):
        """Run the agent with streaming output"""
        if not self.graph:
            raise ValueError("Graph not initialized. Call initialize() first.")

        print(f"\n💬 User: {user_message}")
        print("🤔 Agent is thinking...\n")

        # Create initial state
        initial_state = {"messages": [HumanMessage(content=user_message)]}

        # Stream the graph execution
        async for event in self.graph.astream(initial_state, stream_mode="values"):
            messages = event.get("messages", [])
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage):
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for tool_call in last_message.tool_calls:
                            print(f"🔧 Calling tool: {tool_call['name']}")
                            print(f"   Args: {tool_call['args']}")
                    elif last_message.content:
                        print(f"🤖 Agent: {last_message.content}\n")


async def main():
    """Main function to demonstrate the client"""

    # Initialize the client
    client = MCPLangGraphClient(mcp_server_url="http://0.0.0.0:8002/sse")

    try:
        # Connect to MCP server
        async with httpx.AsyncClient() as http_client:
            async with sse_client("http://0.0.0.0:8002/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()

                    # List and convert tools
                    tools_response = await session.list_tools()
                    print(f"✅ Connected! Found {len(tools_response.tools)} tools:")
                    for tool in tools_response.tools:
                        print(f"  📦 {tool.name}: {tool.description}")

                    # Create LangChain tools with proper closures
                    from langchain_core.tools import StructuredTool

                    langchain_tools = []
                    for mcp_tool in tools_response.tools:
                        # Create a closure that captures the tool name
                        def make_tool_func(tool_name):
                            async def tool_func(**kwargs):
                                result = await session.call_tool(
                                    tool_name, arguments=kwargs
                                )
                                if result.content:
                                    content = result.content[0]
                                    return (
                                        content.text
                                        if hasattr(content, "text")
                                        else str(content)
                                    )
                                return str(result)

                            return tool_func

                        # Use StructuredTool which better handles async functions
                        tool = StructuredTool.from_function(
                            coroutine=make_tool_func(mcp_tool.name),
                            name=mcp_tool.name,
                            description=mcp_tool.description
                            or f"Execute {mcp_tool.name}",
                        )
                        langchain_tools.append(tool)

                    # Initialize LLM with tools
                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0,
                        api_key=os.environ["OPENAI_API_KEY"],
                    ).bind_tools(langchain_tools)

                    # Build graph
                    async def call_model(state: AgentState):
                        response = await llm.ainvoke(state["messages"])
                        return {"messages": [response]}

                    def should_continue(state: AgentState):
                        last_message = state["messages"][-1]
                        if (
                            hasattr(last_message, "tool_calls")
                            and last_message.tool_calls
                        ):
                            return "tools"
                        return "end"

                    workflow = StateGraph(AgentState)
                    workflow.add_node("agent", call_model)
                    workflow.add_node("tools", ToolNode(langchain_tools))
                    workflow.add_edge(START, "agent")
                    workflow.add_conditional_edges(
                        "agent", should_continue, {"tools": "tools", "end": END}
                    )
                    workflow.add_edge("tools", "agent")

                    graph = workflow.compile()
                    print("\n✅ LangGraph compiled successfully\n")

                    # Example queries
                    queries = [
                        "Get my latest 3 emails from Gmail",
                        "Get the Instagram profile for user 'celebrity'",
                        "Check my inbox for any emails about 'meeting' and also get the Instagram profile for 'verified_user'",
                    ]

                    for query in queries:
                        print(f"{'=' * 60}")
                        print(f"💬 User: {query}")
                        print(f"{'=' * 60}")

                        initial_state = {"messages": [HumanMessage(content=query)]}

                        async for event in graph.astream(
                            initial_state, stream_mode="values"
                        ):
                            messages = event.get("messages", [])
                            if messages:
                                last_message = messages[-1]
                                if isinstance(last_message, AIMessage):
                                    if (
                                        hasattr(last_message, "tool_calls")
                                        and last_message.tool_calls
                                    ):
                                        for tool_call in last_message.tool_calls:
                                            print(
                                                f"\n🔧 Calling tool: {tool_call['name']}"
                                            )
                                            print(f"   Args: {tool_call['args']}")
                                    elif last_message.content:
                                        print(f"\n🤖 Agent: {last_message.content}")

                        print("\n")
                        await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the client
    asyncio.run(main())
