# Reddit MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with read-only access to Reddit's API. This server enables Claude and other MCP-compatible AI assistants to browse subreddits, read posts and comments, search Reddit, and get user/subreddit information.

## Features

### 🛠️ Available Tools

- **`get_subreddit_posts`** - Browse posts from any subreddit with flexible sorting options
- **`get_post_details`** - Get detailed information about specific posts
- **`get_post_comments`** - Read comments from any post with various sorting methods
- **`search_reddit`** - Search across Reddit or within specific subreddits
- **`get_user_profile`** - View public user profiles and recent activity
- **`get_subreddit_info`** - Get subreddit details, rules, and moderation info

### ✨ Key Benefits

- **Read-only access** - Safe browsing without posting capabilities
- **Comprehensive error handling** - Graceful handling of API limits and errors
- **Flexible parameters** - Customizable limits, sorting, and filtering options
- **Rich formatting** - Well-structured responses with all relevant metadata
- **Rate limit compliant** - Respects Reddit's API guidelines

## Installation

### Prerequisites

1. **Reddit API Credentials**
   - Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
   - Click "Create another app..."
   - Choose "script" as the app type
   - Set redirect URI to `http://localhost:8080`
   - Save your Client ID and Client Secret

2. **Python Environment**
   - Python 3.8 or higher
   - pip package manager

### Setup Steps

1. **Clone and install:**
```bash
git clone https://github.com/yourusername/reddit-mcp-server.git
cd reddit-mcp-server
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Reddit API credentials
```

3. **Environment variables:**
```env
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=RedditMCPServer/1.0.0
```

### Install via pip (Coming Soon)
```bash
pip install reddit-mcp-server
```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "reddit": {
      "command": "python",
      "args": ["/path/to/reddit-mcp-server/server.py"],
      "env": {
        "REDDIT_CLIENT_ID": "your_client_id",
        "REDDIT_CLIENT_SECRET": "your_client_secret",
        "REDDIT_USER_AGENT": "RedditMCPServer/1.0.0"
      }
    }
  }
}
```

### Standalone Usage

```bash
python server.py
```

## Tool Examples

### Get Subreddit Posts
Ask Claude: *"Get the top 10 hot posts from r/python"*

This uses: `get_subreddit_posts(subreddit="python", sort="hot", limit=10)`

### Search Reddit
Ask Claude: *"Search for posts about machine learning in r/MachineLearning from the past week"*

This uses: `search_reddit(query="machine learning", subreddit="MachineLearning", time_filter="week")`

### Get Post Details
Ask Claude: *"Get details and comments for this Reddit post: [post URL]"*

This uses: `get_post_details(post_id="url", include_comments=true)`

### User Profile
Ask Claude: *"What can you tell me about Reddit user spez?"*

This uses: `get_user_profile(username="spez")`

## Tool Reference

### `get_subreddit_posts`
Browse posts from a specific subreddit.

**Parameters:**
- `subreddit` (required): Subreddit name without "r/"
- `sort`: "hot", "new", "rising", "top" (default: "hot")  
- `time_filter`: For "top" sort - "hour", "day", "week", "month", "year", "all"
- `limit`: Number of posts (1-100, default: 25)

### `get_post_details`
Get comprehensive information about a specific post.

**Parameters:**
- `post_id` (required): Reddit post ID or full URL
- `include_comments`: Include top comments (default: false)

### `get_post_comments`
Retrieve comments from a post with flexible sorting.

**Parameters:**
- `post_id` (required): Reddit post ID or full URL
- `sort`: "best", "top", "new", "controversial" (default: "best")
- `limit`: Number of comments (1-100, default: 50)

### `search_reddit`
Search Reddit posts with advanced filtering.

**Parameters:**
- `query` (required): Search terms
- `subreddit`: Limit to specific subreddit (optional)
- `sort`: "relevance", "hot", "top", "new", "comments" (default: "relevance")
- `time_filter`: "hour", "day", "week", "month", "year", "all" (default: "all")
- `limit`: Number of results (1-100, default: 25)

### `get_user_profile`
Get public information about a Reddit user.

**Parameters:**
- `username` (required): Reddit username without "u/"

### `get_subreddit_info`
Get detailed information about a subreddit.

**Parameters:**
- `subreddit` (required): Subreddit name without "r/"

## Error Handling

The server includes comprehensive error handling for:
- Invalid subreddit names
- Non-existent posts or users
- Reddit API rate limits
- Network connectivity issues
- Malformed requests

All errors are returned as descriptive text messages to help users understand what went wrong.

## Rate Limiting & Best Practices

- The server respects Reddit's API rate limits (60 requests per minute)
- Implements proper error handling for rate limit exceeded scenarios
- Uses efficient PRAW configurations to minimize API calls
- Includes appropriate User-Agent strings for identification

## Security & Privacy

- **Read-only access**: Cannot post, comment, or modify any Reddit content
- **No authentication storage**: Uses app-only authentication (no user tokens)
- **Privacy-focused**: Only accesses publicly available Reddit data
- **No data persistence**: Does not store or cache any Reddit data locally

## Development

### Project Structure
```
reddit-mcp-server/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── setup.py              # Package configuration
├── README.md             # Documentation
└── tests/                # Test suite (coming soon)
```

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Troubleshooting

### Common Issues

**"Invalid credentials" error:**
- Verify your Reddit API credentials in the `.env` file
- Ensure the Reddit app is configured as "script" type
- Check that the User-Agent string is properly formatted

**"Subreddit not found" error:**
- Verify the subreddit name is correct (without "r/" prefix)
- Check if the subreddit is private or banned
- Ensure the subreddit name is spelled correctly

**Rate limit errors:**
- Wait a few minutes before making more requests
- Consider reducing the `limit` parameter in your requests
- The server automatically handles most rate limiting scenarios

**MCP connection issues:**
- Verify the path to `server.py` in your Claude configuration
- Check that all required environment variables are set
- Ensure Python and dependencies are properly installed

### Debug Mode

To run the server with detailed logging:
```bash
export MCP_DEBUG=1
python server.py
```

## Changelog

### Version 1.0.0
- Initial release
- Core Reddit API tools implementation
- Comprehensive error handling
- Production-ready MCP server

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/reddit-mcp-server/issues)
- **MCP Community**: [MCP Servers Directory](https://mcpservers.org)
- **Reddit API**: [PRAW Documentation](https://praw.readthedocs.io/)

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [PRAW (Python Reddit API Wrapper)](https://github.com/praw-dev/praw)

---

**Built for the MCP community**