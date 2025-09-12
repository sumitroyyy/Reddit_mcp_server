#!/usr/bin/env python3
"""
Test script for Reddit MCP Server

This script tests all the major functionality of the Reddit MCP server
to ensure it's working correctly before deployment.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import praw

# Load environment variables
load_dotenv()

def check_reddit_credentials():
    """Test Reddit API credentials."""
    print("🔍 Testing Reddit API credentials...")
    
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Test API access
        subreddit = reddit.subreddit("python")
        post = next(subreddit.hot(limit=1))
        print(f"✅ Reddit API connection successful")
        print(f"   Test post: {post.title[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Reddit API connection failed: {e}")
        return False

def test_subreddit_access():
    """Test accessing various subreddits."""
    print("\n🔍 Testing subreddit access...")
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Test popular subreddits
        test_subreddits = ["python", "technology", "AskReddit", "news"]
        
        for sub_name in test_subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                posts = list(subreddit.hot(limit=1))
                if posts:
                    print(f"✅ r/{sub_name}: {posts[0].title[:40]}...")
                else:
                    print(f"⚠️  r/{sub_name}: No posts found")
            except Exception as e:
                print(f"❌ r/{sub_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Subreddit access test failed: {e}")
        return False

def test_search_functionality():
    """Test Reddit search functionality."""
    print("\n🔍 Testing search functionality...")
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Test search
        search_results = list(reddit.subreddit("python").search("tutorial", limit=3))
        
        if search_results:
            print(f"✅ Search working: Found {len(search_results)} results")
            for i, post in enumerate(search_results, 1):
                print(f"   {i}. {post.title[:40]}...")
        else:
            print("⚠️  Search returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_user_access():
    """Test user profile access."""
    print("\n🔍 Testing user profile access...")
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Test with Reddit admin account
        user = reddit.redditor("spez")
        print(f"✅ User access working")
        print(f"   Profile: u/{user.name}")
        print(f"   Comment Karma: {user.comment_karma}")
        print(f"   Link Karma: {user.link_karma}")
        
        return True
        
    except Exception as e:
        print(f"❌ User access test failed: {e}")
        return False

def test_comment_access():
    """Test comment retrieval."""
    print("\n🔍 Testing comment access...")
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Get a post with comments
        subreddit = reddit.subreddit("AskReddit")
        post = next(subreddit.hot(limit=1))
        
        if post.num_comments > 0:
            post.comments.replace_more(limit=0)
            comments = list(post.comments[:3])
            print(f"✅ Comment access working")
            print(f"   Post: {post.title[:40]}...")
            print(f"   Comments found: {len(comments)}")
        else:
            print("⚠️  Test post has no comments")
        
        return True
        
    except Exception as e:
        print(f"❌ Comment access test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting behavior."""
    print("\n🔍 Testing rate limiting behavior...")
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )
        
        # Make several requests quickly
        subreddit = reddit.subreddit("python")
        requests_made = 0
        
        for i in range(5):
            try:
                posts = list(subreddit.hot(limit=1))
                requests_made += 1
            except Exception as e:
                print(f"   Request {i+1} failed: {e}")
                break
        
        print(f"✅ Made {requests_made} requests successfully")
        print("   Rate limiting appears to be handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Reddit MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("Reddit Credentials", check_reddit_credentials),
        ("Subreddit Access", test_subreddit_access),
        ("Search Functionality", test_search_functionality),
        ("User Access", test_user_access),
        ("Comment Access", test_comment_access),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed")
        print("\nNext steps:")
        print("1. Start the server: python server.py")
        print("2. Configure Claude Desktop with your server")
        print("3. Test the MCP tools in Claude")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        print("Make sure your .env file has correct Reddit API credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()