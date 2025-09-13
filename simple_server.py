def list_flairs(subreddit_name):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        check_for_async=False
    )
    subreddit = reddit.subreddit(subreddit_name)
    print(f"Available flairs for r/{subreddit_name}:")
    for flair in subreddit.flair.link_templates:
        print(flair)
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


def get_top_posts(subreddit_name, limit=5):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        check_for_async=False
    )
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.hot(limit=limit):
        posts.append(f"{post.title} (Score: {post.score}) - {post.url}")
    return posts

def post_to_reddit(subreddit_name, title, body, flair_id=None):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        check_for_async=False
    )
    subreddit = reddit.subreddit(subreddit_name)
    if flair_id:
        submission = subreddit.submit(title, selftext=body, flair_id=flair_id)
    else:
        submission = subreddit.submit(title, selftext=body)
    return submission.url


def main():
    print("Simple Reddit CLI Server started. Type your command:")
    while True:
        try:
            line = input("> ").strip()
            print(f"[DEBUG] Received line: '{line}'")
            cmd = ' '.join(line.lower().split())
            print(f"[DEBUG] Parsed command: '{cmd}'")
            if cmd.startswith("list flairs for"):
                # Example: list flairs for python
                parts = line.split()
                if len(parts) >= 4:
                    subreddit = parts[-1]
                    list_flairs(subreddit)
                else:
                    print("Usage: list flairs for <subreddit>")
            elif line.startswith("get me top"):
                # Example: get me top 5 post from python
                parts = line.split()
                try:
                    limit = int(parts[3])
                    subreddit = parts[-1]
                except Exception:
                    print("Usage: get me top <N> post from <subreddit>")
                    continue
                posts = get_top_posts(subreddit, limit)
                for post in posts:
                    print(post)
            elif line.startswith("post my first post on reddit"):
                # Example: post my first post on reddit "hello i am Roy's mcp" to python with flair <flair_id>
                import re
                match = re.match(r'post my first post on reddit "(.+)" to (\w+)(?: with flair (\w+))?', line)
                if match:
                    body = match.group(1)
                    subreddit = match.group(2)
                    flair_id = match.group(3)
                    title = "My First Post from MCP"
                    try:
                        url = post_to_reddit(subreddit, title, body, flair_id)
                        print(f"Posted: {url}")
                    except Exception as e:
                        print(f"Error posting: {e}")
                else:
                    print("Usage: post my first post on reddit \"<body>\" to <subreddit> [with flair <flair_id>]")
            else:
                print("Unknown command. Try: get me top 5 post from python or post my first post on reddit \"hello\" to python")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()