from fastmcp import FastMCP
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("Slack MCP Server")

@mcp.tool()
def send_message(channel: str, text: str, thread_ts: Optional[str] = None) -> dict:
    """
    Send a message to a Slack channel.
    
    Args:
        channel: The channel name or ID to send the message to
        text: The content of the message to send
        thread_ts: Optional thread timestamp to reply to a thread
    
    Returns:
        Dictionary containing message confirmation
    """
    # Dummy implementation - returns mock data
    return {
        "success": True,
        "message": {
            "ts": "1732187400.123456",
            "channel": channel,
            "text": text,
            "user": "U12345678",
            "username": "demo_user",
            "thread_ts": thread_ts,
            "type": "message",
            "created_at": "2025-11-22T10:30:00Z"
        },
        "message_sent": "Message sent successfully!"
    }


@mcp.tool()
def get_channel_messages(channel: str, limit: int = 10) -> dict:
    """
    Get recent messages from a Slack channel.
    
    Args:
        channel: The channel name or ID to get messages from
        limit: Maximum number of messages to retrieve (default: 10)
    
    Returns:
        Dictionary containing channel messages
    """
    # Dummy implementation - returns mock data
    messages = []
    
    for i in range(min(limit, 5)):
        messages.append({
            "ts": f"173218{7400 - (i * 100)}.{123456 + i}",
            "user": f"U1234567{i}",
            "username": f"team_member_{i+1}",
            "text": f"This is a sample message {i+1} in the {channel} channel",
            "type": "message",
            "reactions": [
                {"name": "thumbsup", "count": 3 - i if i < 3 else 1},
                {"name": "eyes", "count": 2 - i if i < 2 else 1}
            ] if i % 2 == 0 else [],
            "thread_count": (5 - i) if i < 3 else 0,
            "created_at": f"2025-11-{22-i:02d}T{10+i}:00:00Z"
        })
    
    return {
        "success": True,
        "channel": channel,
        "total_messages": len(messages),
        "messages": messages
    }


@mcp.tool()
def get_thread_replies(channel: str, thread_ts: str, limit: int = 10) -> dict:
    """
    Get replies to a thread in a Slack channel.
    
    Args:
        channel: The channel name or ID
        thread_ts: The timestamp of the parent message
        limit: Maximum number of replies to retrieve (default: 10)
    
    Returns:
        Dictionary containing thread replies
    """
    # Dummy implementation - returns mock data
    replies = []
    
    # Add parent message
    replies.append({
        "ts": thread_ts,
        "user": "U12345670",
        "username": "thread_starter",
        "text": "This is the parent message that started the thread",
        "type": "message",
        "is_parent": True,
        "reply_count": min(limit - 1, 4),
        "created_at": "2025-11-21T09:00:00Z"
    })
    
    # Add replies
    for i in range(min(limit - 1, 4)):
        replies.append({
            "ts": f"{thread_ts}.{i+1}",
            "user": f"U1234567{i+1}",
            "username": f"responder_{i+1}",
            "text": f"This is reply {i+1} to the thread",
            "type": "message",
            "thread_ts": thread_ts,
            "created_at": f"2025-11-21T{9+i+1}:00:00Z"
        })
    
    return {
        "success": True,
        "channel": channel,
        "thread_ts": thread_ts,
        "total_replies": len(replies),
        "replies": replies
    }


@mcp.tool()
def list_channels() -> dict:
    """
    List all available Slack channels.
    
    Returns:
        Dictionary containing list of channels
    """
    # Dummy implementation - returns mock data
    channels = [
        {
            "id": "C12345678",
            "name": "general",
            "is_channel": True,
            "is_private": False,
            "is_archived": False,
            "members_count": 45,
            "topic": "Company-wide announcements and general discussions",
            "purpose": "This channel is for team-wide communication"
        },
        {
            "id": "C23456789",
            "name": "engineering",
            "is_channel": True,
            "is_private": False,
            "is_archived": False,
            "members_count": 23,
            "topic": "Engineering team discussions and updates",
            "purpose": "For all engineering-related conversations"
        },
        {
            "id": "C34567890",
            "name": "random",
            "is_channel": True,
            "is_private": False,
            "is_archived": False,
            "members_count": 38,
            "topic": "Non-work banter and water cooler conversation",
            "purpose": "A place for random things"
        },
        {
            "id": "C45678901",
            "name": "product",
            "is_channel": True,
            "is_private": False,
            "is_archived": False,
            "members_count": 15,
            "topic": "Product discussions and roadmap planning",
            "purpose": "Product team collaboration"
        },
        {
            "id": "C56789012",
            "name": "project-alpha",
            "is_channel": True,
            "is_private": True,
            "is_archived": False,
            "members_count": 8,
            "topic": "Project Alpha - Confidential",
            "purpose": "Private channel for Project Alpha team"
        }
    ]
    
    return {
        "success": True,
        "total_channels": len(channels),
        "channels": channels
    }


@mcp.tool()
def get_user_profile(user_id: Optional[str] = None) -> dict:
    """
    Get Slack user profile information.
    
    Args:
        user_id: Optional user ID. If not provided, returns current user's profile
    
    Returns:
        Dictionary containing user profile data
    """
    # Dummy implementation - returns mock data
    if not user_id:
        user_id = "U12345678"
    
    return {
        "success": True,
        "user": {
            "id": user_id,
            "name": "demo_user",
            "real_name": "Demo User",
            "display_name": "Demo",
            "email": "demo@company.com",
            "title": "Senior Software Engineer",
            "phone": "+1-555-0123",
            "status_text": "In a meeting",
            "status_emoji": ":calendar:",
            "team_id": "T12345678",
            "is_admin": False,
            "is_owner": False,
            "is_bot": False,
            "timezone": "America/Los_Angeles",
            "timezone_offset": -28800,
            "profile_image": "https://example.com/avatars/demo_user.jpg"
        }
    }


@mcp.tool()
def search_messages(query: str, count: int = 10) -> dict:
    """
    Search for messages across all Slack channels.
    
    Args:
        query: The search query
        count: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing search results
    """
    # Dummy implementation - returns mock data
    results = []
    
    for i in range(min(count, 5)):
        results.append({
            "ts": f"173218{7000 + (i * 100)}.{111111 + i}",
            "channel": f"C{12345678 + i}",
            "channel_name": ["general", "engineering", "random", "product", "support"][i % 5],
            "user": f"U1234567{i}",
            "username": f"user_{i+1}",
            "text": f"Message containing '{query}' - Sample result {i+1}",
            "permalink": f"https://company.slack.com/archives/C{12345678 + i}/p{173218}{7000 + (i * 100)}{111111 + i}",
            "created_at": f"2025-11-{15+i:02d}T{10+i}:00:00Z"
        })
    
    return {
        "success": True,
        "query": query,
        "total_results": len(results),
        "results": results
    }


@mcp.tool()
def add_reaction(channel: str, timestamp: str, reaction: str) -> dict:
    """
    Add a reaction emoji to a Slack message.
    
    Args:
        channel: The channel ID where the message is located
        timestamp: The timestamp of the message
        reaction: The emoji name (without colons, e.g., 'thumbsup')
    
    Returns:
        Dictionary containing reaction confirmation
    """
    # Dummy implementation - returns mock data
    return {
        "success": True,
        "reaction": {
            "channel": channel,
            "timestamp": timestamp,
            "reaction": reaction,
            "user": "U12345678"
        },
        "message": f"Reaction :{reaction}: added successfully!"
    }


@mcp.tool()
def get_workspace_info() -> dict:
    """
    Get information about the Slack workspace.
    
    Returns:
        Dictionary containing workspace information
    """
    # Dummy implementation - returns mock data
    return {
        "success": True,
        "workspace": {
            "id": "T12345678",
            "name": "Demo Company",
            "domain": "democompany",
            "email_domain": "democompany.com",
            "icon": "https://example.com/workspaces/demo.png",
            "total_members": 150,
            "total_channels": 45,
            "total_public_channels": 32,
            "total_private_channels": 13,
            "created_at": "2020-01-15T10:00:00Z",
            "plan": "Standard"
        }
    }


# Run the server with HTTP streaming support
if __name__ == "__main__":
    # Start HTTP server on port 8003 with SSE (Server-Sent Events) support
    mcp.run(transport="sse", port=8003, host="0.0.0.0")
