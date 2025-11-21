from fastmcp import FastMCP
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("Twitter MCP Server")

@mcp.tool()
def send_tweet(text: str) -> dict:
    """
    Send a tweet.
    
    Args:
        text: The content of the tweet to send
    
    Returns:
        Dictionary containing tweet confirmation
    """
    # Dummy implementation - returns mock data
    return {
        "success": True,
        "tweet": {
            "id": "tweet_12345",
            "text": text,
            "created_at": "2025-11-21T10:30:00Z",
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "views": 12
        },
        "message": "Tweet sent successfully!"
    }


@mcp.tool()
def get_comments(tweet_id: str, max_results: int = 10) -> dict:
    """
    Get comments/replies on a tweet.
    
    Args:
        tweet_id: The ID of the tweet to get comments for
        max_results: Maximum number of comments to retrieve (default: 10)
    
    Returns:
        Dictionary containing comments data
    """
    # Dummy implementation - returns mock data
    comments = []
    
    for i in range(min(max_results, 5)):
        comments.append({
            "id": f"comment_{i+1}",
            "user": f"@user{i+1}",
            "text": f"This is a sample comment {i+1} on tweet {tweet_id}",
            "likes": 50 - (i * 10),
            "created_at": f"2025-11-{21-i:02d}T{10+i}:00:00Z",
            "verified": i == 0
        })
    
    return {
        "success": True,
        "tweet_id": tweet_id,
        "total_comments": len(comments),
        "comments": comments
    }


@mcp.tool()
def get_profile_data() -> dict:
    """
    Get Twitter profile data for the authenticated user.
    
    Returns:
        Dictionary containing profile data
    """
    # Dummy implementation - returns mock data
    return {
        "success": True,
        "profile": {
            "username": "demo_user",
            "display_name": "Demo User",
            "bio": "Software developer | Tech enthusiast | Coffee lover ☕",
            "profile_image": "https://example.com/profiles/demo_user.jpg",
            "banner_image": "https://example.com/banners/demo_user.jpg",
            "followers": 2450,
            "following": 389,
            "tweets": 1823,
            "verified": False,
            "created_at": "2020-03-15",
            "location": "San Francisco, CA",
            "website": "https://example.com"
        }
    }


@mcp.tool()
def get_posts(max_results: int = 10) -> dict:
    """
    Get recent tweets/posts from the user's timeline.
    
    Args:
        max_results: Maximum number of posts to retrieve (default: 10)
    
    Returns:
        Dictionary containing posts data
    """
    # Dummy implementation - returns mock data
    posts = []
    
    for i in range(min(max_results, 5)):
        posts.append({
            "id": f"post_{i+1}",
            "user": "@demo_user",
            "text": f"This is sample tweet number {i+1}. Having a great day! 🚀",
            "created_at": f"2025-11-{21-i:02d}T{14+i}:30:00Z",
            "likes": 250 - (i * 40),
            "retweets": 45 - (i * 8),
            "replies": 12 - (i * 2),
            "views": 5000 - (i * 800),
            "has_media": i % 2 == 0,
            "media_type": "photo" if i % 2 == 0 else None
        })
    
    return {
        "success": True,
        "total_posts": len(posts),
        "posts": posts
    }


# Run the server with HTTP streaming support
if __name__ == "__main__":
    # Start HTTP server on port 8000 with SSE (Server-Sent Events) support
    mcp.run(transport="sse", port=8002, host="0.0.0.0")