#!/usr/bin/env python3
import asyncio
import os
import json
from dotenv import load_dotenv
import praw

load_dotenv()

# Simple MCP server that just handles JSON-RPC over stdio
async def handle_reddit_request(method, params):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        check_for_async=False
    )
    
    if method == "get_subreddit_posts":
        subreddit = reddit.subreddit(params.get("subreddit", "python"))
        posts = []
        for post in subreddit.hot(limit=5):
            posts.append({
                "title": post.title,
                "score": post.score,
                "author": str(post.author) if post.author else "[deleted]",
                "url": post.url
            })
        return {"posts": posts}
    
    return {"error": "Unknown method"}

async def main():
    print("Simple Reddit MCP Server starting...", flush=True)
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, input)
            if line.strip():
                request = json.loads(line)
                result = await handle_reddit_request(request.get("method"), request.get("params", {}))
                response = {"id": request.get("id"), "result": result}
                print(json.dumps(response), flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())