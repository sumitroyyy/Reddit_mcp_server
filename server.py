#!/usr/bin/env python3
"""
Reddit MCP Server

A Model Context Protocol server that provides access to Reddit's API.
Allows AI assistants to browse subreddits, read posts, get comments, and search Reddit.
"""

import asyncio
import os
from typing import Any, Sequence
from dotenv import load_dotenv
import praw
from praw.exceptions import RedditAPIException, PRAWException
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Load environment variables
load_dotenv()

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "RedditMCPServer/1.0.0"),
    check_for_async=False
)

# Create MCP server instance
server = Server("reddit-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Reddit tools."""
    return [
        types.Tool(
            name="get_subreddit_posts",
            description="Get posts from a specific subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort method: hot, new, rising, top",
                        "enum": ["hot", "new", "rising", "top"],
                        "default": "hot"
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter for 'top' sort: hour, day, week, month, year, all",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "day"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25
                    }
                },
                "required": ["subreddit"]
            }
        ),
        types.Tool(
            name="get_post_details",
            description="Get detailed information about a specific Reddit post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID or full URL"
                    },
                    "include_comments": {
                        "type": "boolean",
                        "description": "Whether to include top-level comments",
                        "default": False
                    }
                },
                "required": ["post_id"]
            }
        ),
        types.Tool(
            name="get_post_comments",
            description="Get comments from a specific Reddit post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Reddit post ID or full URL"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Comment sort method: best, top, new, controversial",
                        "enum": ["best", "top", "new", "controversial"],
                        "default": "best"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of comments to fetch (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50
                    }
                },
                "required": ["post_id"]
            }
        ),
        types.Tool(
            name="search_reddit",
            description="Search Reddit for posts matching a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "subreddit": {
                        "type": "string",
                        "description": "Limit search to specific subreddit (optional)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort method: relevance, hot, top, new, comments",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance"
                    },
                    "time_filter": {
                        "type": "string",
                        "description": "Time filter: hour, day, week, month, year, all",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_user_profile",
            description="Get public information about a Reddit user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Reddit username (without u/)"
                    }
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_subreddit_info",
            description="Get information about a subreddit",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Name of the subreddit (without r/)"
                    }
                },
                "required": ["subreddit"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool execution requests."""
    
    try:
        if name == "get_subreddit_posts":
            return await get_subreddit_posts(arguments)
        elif name == "get_post_details":
            return await get_post_details(arguments)
        elif name == "get_post_comments":
            return await get_post_comments(arguments)
        elif name == "search_reddit":
            return await search_reddit(arguments)
        elif name == "get_user_profile":
            return await get_user_profile(arguments)
        elif name == "get_subreddit_info":
            return await get_subreddit_info(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except RedditAPIException as e:
        error_msg = f"Reddit API Error: {e.message}"
        return [types.TextContent(type="text", text=error_msg)]
    except RedditException as e:
        error_msg = f"Reddit Error: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]

async def get_subreddit_posts(args: dict[str, Any]) -> list[types.TextContent]:
    """Get posts from a subreddit."""
    subreddit_name = args["subreddit"]
    sort_method = args.get("sort", "hot")
    time_filter = args.get("time_filter", "day")
    limit = args.get("limit", 25)
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Get posts based on sort method
        if sort_method == "hot":
            posts = subreddit.hot(limit=limit)
        elif sort_method == "new":
            posts = subreddit.new(limit=limit)
        elif sort_method == "rising":
            posts = subreddit.rising(limit=limit)
        elif sort_method == "top":
            posts = subreddit.top(time_filter=time_filter, limit=limit)
        else:
            posts = subreddit.hot(limit=limit)
        
        results = []
        for post in posts:
            post_info = {
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "url": post.url,
                "permalink": f"https://reddit.com{post.permalink}",
                "id": post.id,
                "selftext": post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext,
                "subreddit": str(post.subreddit),
                "flair": post.link_flair_text,
                "is_self": post.is_self,
                "over_18": post.over_18
            }
            results.append(post_info)
        
        # Format results
        output = f"## Posts from r/{subreddit_name} (sorted by {sort_method})\n\n"
        for i, post in enumerate(results, 1):
            output += f"### {i}. {post['title']}\n"
            output += f"- **Author:** u/{post['author']}\n"
            output += f"- **Score:** {post['score']} ({int(post['upvote_ratio']*100)}% upvoted)\n"
            output += f"- **Comments:** {post['num_comments']}\n"
            output += f"- **URL:** {post['url']}\n"
            output += f"- **Reddit Link:** {post['permalink']}\n"
            if post['flair']:
                output += f"- **Flair:** {post['flair']}\n"
            if post['selftext']:
                output += f"- **Text:** {post['selftext']}\n"
            output += f"- **NSFW:** {'Yes' if post['over_18'] else 'No'}\n"
            output += f"- **Post ID:** {post['id']}\n\n"
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error fetching posts from r/{subreddit_name}: {str(e)}")]

async def get_post_details(args: dict[str, Any]) -> list[types.TextContent]:
    """Get detailed information about a specific post."""
    post_id = args["post_id"]
    include_comments = args.get("include_comments", False)
    
    try:
        # Handle both post ID and full URL
        if "reddit.com" in post_id:
            submission = reddit.submission(url=post_id)
        else:
            submission = reddit.submission(id=post_id)
        
        # Get post details
        output = f"## {submission.title}\n\n"
        output += f"**Author:** u/{submission.author if submission.author else '[deleted]'}\n"
        output += f"**Subreddit:** r/{submission.subreddit}\n"
        output += f"**Score:** {submission.score} ({int(submission.upvote_ratio*100)}% upvoted)\n"
        output += f"**Comments:** {submission.num_comments}\n"
        output += f"**Created:** {submission.created_utc}\n"
        output += f"**URL:** {submission.url}\n"
        output += f"**Permalink:** https://reddit.com{submission.permalink}\n"
        if submission.link_flair_text:
            output += f"**Flair:** {submission.link_flair_text}\n"
        output += f"**NSFW:** {'Yes' if submission.over_18 else 'No'}\n\n"
        
        if submission.selftext:
            output += f"### Post Content\n{submission.selftext}\n\n"
        
        if include_comments:
            output += "### Top Comments\n\n"
            submission.comments.replace_more(limit=0)
            for i, comment in enumerate(submission.comments[:10], 1):
                if hasattr(comment, 'body'):
                    output += f"**{i}.** u/{comment.author if comment.author else '[deleted]'} "
                    output += f"(Score: {comment.score})\n"
                    comment_body = comment.body[:300] + "..." if len(comment.body) > 300 else comment.body
                    output += f"{comment_body}\n\n"
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error fetching post details: {str(e)}")]

async def get_post_comments(args: dict[str, Any]) -> list[types.TextContent]:
    """Get comments from a specific post."""
    post_id = args["post_id"]
    sort_method = args.get("sort", "best")
    limit = args.get("limit", 50)
    
    try:
        # Handle both post ID and full URL
        if "reddit.com" in post_id:
            submission = reddit.submission(url=post_id)
        else:
            submission = reddit.submission(id=post_id)
        
        submission.comment_sort = sort_method
        submission.comments.replace_more(limit=0)
        
        output = f"## Comments for: {submission.title}\n\n"
        output += f"**Post by:** u/{submission.author if submission.author else '[deleted]'} in r/{submission.subreddit}\n"
        output += f"**Total Comments:** {submission.num_comments}\n"
        output += f"**Sorted by:** {sort_method}\n\n"
        
        comment_count = 0
        for comment in submission.comments:
            if comment_count >= limit:
                break
            if hasattr(comment, 'body') and comment.body != '[deleted]':
                comment_count += 1
                output += f"### Comment {comment_count}\n"
                output += f"**Author:** u/{comment.author if comment.author else '[deleted]'}\n"
                output += f"**Score:** {comment.score}\n"
                output += f"**Content:** {comment.body}\n\n"
                
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error fetching comments: {str(e)}")]

async def search_reddit(args: dict[str, Any]) -> list[types.TextContent]:
    """Search Reddit for posts matching a query."""
    query = args["query"]
    subreddit_name = args.get("subreddit")
    sort_method = args.get("sort", "relevance")
    time_filter = args.get("time_filter", "all")
    limit = args.get("limit", 25)
    
    try:
        if subreddit_name:
            subreddit = reddit.subreddit(subreddit_name)
            search_results = subreddit.search(query, sort=sort_method, time_filter=time_filter, limit=limit)
            search_scope = f"r/{subreddit_name}"
        else:
            search_results = reddit.subreddit("all").search(query, sort=sort_method, time_filter=time_filter, limit=limit)
            search_scope = "All of Reddit"
        
        output = f"## Search Results for '{query}' in {search_scope}\n\n"
        output += f"**Sort:** {sort_method} | **Time Filter:** {time_filter} | **Limit:** {limit}\n\n"
        
        results = []
        for post in search_results:
            results.append({
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "subreddit": str(post.subreddit),
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "permalink": f"https://reddit.com{post.permalink}",
                "id": post.id,
                "selftext": post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext
            })
        
        if not results:
            return [types.TextContent(type="text", text=f"No results found for '{query}'")]
        
        for i, post in enumerate(results, 1):
            output += f"### {i}. {post['title']}\n"
            output += f"- **Subreddit:** r/{post['subreddit']}\n"
            output += f"- **Author:** u/{post['author']}\n"
            output += f"- **Score:** {post['score']} | **Comments:** {post['num_comments']}\n"
            output += f"- **URL:** {post['url']}\n"
            output += f"- **Reddit Link:** {post['permalink']}\n"
            if post['selftext']:
                output += f"- **Preview:** {post['selftext']}\n"
            output += f"- **Post ID:** {post['id']}\n\n"
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error searching Reddit: {str(e)}")]

async def get_user_profile(args: dict[str, Any]) -> list[types.TextContent]:
    """Get public information about a Reddit user."""
    username = args["username"]
    
    try:
        user = reddit.redditor(username)
        
        output = f"## User Profile: u/{username}\n\n"
        output += f"**Comment Karma:** {user.comment_karma}\n"
        output += f"**Link Karma:** {user.link_karma}\n"
        output += f"**Account Created:** {user.created_utc}\n"
        output += f"**Has Verified Email:** {'Yes' if user.has_verified_email else 'No'}\n"
        output += f"**Is Employee:** {'Yes' if user.is_employee else 'No'}\n"
        output += f"**Is Gold:** {'Yes' if user.is_gold else 'No'}\n"
        output += f"**Is Mod:** {'Yes' if user.is_mod else 'No'}\n"
        
        if hasattr(user, 'subreddit') and user.subreddit:
            output += f"**Profile Description:** {user.subreddit.public_description}\n"
        
        # Get recent posts
        output += "\n### Recent Posts (Last 10)\n\n"
        try:
            for i, post in enumerate(user.submissions.new(limit=10), 1):
                output += f"{i}. **{post.title}** in r/{post.subreddit} "
                output += f"(Score: {post.score}, Comments: {post.num_comments})\n"
        except Exception:
            output += "Recent posts not available\n"
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error fetching user profile: {str(e)}")]

async def get_subreddit_info(args: dict[str, Any]) -> list[types.TextContent]:
    """Get information about a subreddit."""
    subreddit_name = args["subreddit"]
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        output = f"## r/{subreddit_name}\n\n"
        output += f"**Display Name:** {subreddit.display_name}\n"
        output += f"**Title:** {subreddit.title}\n"
        output += f"**Subscribers:** {subreddit.subscribers:,}\n"
        output += f"**Active Users:** {subreddit.active_user_count}\n"
        output += f"**Created:** {subreddit.created_utc}\n"
        output += f"**NSFW:** {'Yes' if subreddit.over18 else 'No'}\n"
        output += f"**Type:** {subreddit.subreddit_type}\n"
        
        if subreddit.public_description:
            output += f"\n**Description:**\n{subreddit.public_description}\n"
        
        # Rules
        try:
            rules = subreddit.rules()
            if rules:
                output += f"\n### Rules\n\n"
                for i, rule in enumerate(rules, 1):
                    output += f"{i}. **{rule.short_name}**: {rule.description[:200]}...\n"
        except:
            pass
            
        # Moderators
        try:
            mods = list(subreddit.moderator(limit=10))
            if mods:
                output += f"\n### Moderators\n"
                mod_names = [str(mod) for mod in mods if str(mod) != 'None']
                output += ", ".join(mod_names) + "\n"
        except:
            pass
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error fetching subreddit info: {str(e)}")]

async def main():
    """Run the Reddit MCP server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="reddit-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())