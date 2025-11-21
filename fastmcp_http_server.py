from fastmcp import FastMCP
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("Gmail & Instagram MCP Server")

@mcp.tool()
def get_gmail_emails(
    max_results: int = 10,
    query: Optional[str] = None,
    label: Optional[str] = "INBOX"
) -> dict:
    """
    Retrieve emails from Gmail.
    
    Args:
        max_results: Maximum number of emails to retrieve (default: 10)
        query: Search query to filter emails (optional)
        label: Gmail label to filter by (default: INBOX)
    
    Returns:
        Dictionary containing email data
    """
    # Dummy implementation - returns mock data
    emails = []
    
    for i in range(min(max_results, 5)):
        emails.append({
            "id": f"email_{i+1}",
            "from": f"sender{i+1}@example.com",
            "subject": f"Sample Email {i+1}" + (f" matching '{query}'" if query else ""),
            "snippet": f"This is a preview of email {i+1}...",
            "date": f"2025-11-{21-i:02d}",
            "label": label,
            "unread": i % 2 == 0
        })
    
    return {
        "success": True,
        "total_results": len(emails),
        "query": query,
        "label": label,
        "emails": emails
    }


@mcp.tool()
def get_instagram_profile(username: str) -> dict:
    """
    Retrieve Instagram profile information.
    
    Args:
        username: Instagram username to fetch profile for
    
    Returns:
        Dictionary containing profile data
    """
    # Dummy implementation - returns mock data
    profile_data = {
        "success": True,
        "username": username,
        "profile": {
            "full_name": f"{username.title()} User",
            "bio": f"This is the bio for @{username}",
            "profile_picture": f"https://example.com/profiles/{username}.jpg",
            "followers": 15420,
            "following": 892,
            "posts": 234,
            "verified": username.lower() in ["verified_user", "celebrity"],
            "is_private": False,
            "recent_posts": [
                {
                    "id": f"post_1",
                    "caption": "Beautiful sunset! 🌅",
                    "likes": 1205,
                    "comments": 43,
                    "date": "2025-11-20"
                },
                {
                    "id": f"post_2",
                    "caption": "Coffee time ☕",
                    "likes": 892,
                    "comments": 28,
                    "date": "2025-11-18"
                },
                {
                    "id": f"post_3",
                    "caption": "Weekend vibes! 🎉",
                    "likes": 1543,
                    "comments": 67,
                    "date": "2025-11-15"
                }
            ]
        }
    }
    
    return profile_data


# Run the server with HTTP streaming support
if __name__ == "__main__":
    # Start HTTP server on port 8000 with SSE (Server-Sent Events) support
    mcp.run(transport="sse", port=8002, host="0.0.0.0")