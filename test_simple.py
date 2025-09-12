#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
import praw

print("Starting simple test...")

# Load environment variables
load_dotenv()
print("Environment loaded")

# Test Reddit connection
print("Testing Reddit connection...")
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "RedditMCPServer/1.0.0"),
    check_for_async=False
)

try:
    subreddit = reddit.subreddit("python")
    post = next(subreddit.hot(limit=1))
    print(f"Reddit connection successful! Test post: {post.title[:50]}")
except Exception as e:
    print(f"Reddit connection failed: {e}")

print("Simple test completed")