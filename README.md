# Botasaurus MCP Server

This is a Model Context Protocol (MCP) server that provides AI applications with powerful web scraping capabilities using the Botasaurus framework.

## Features

- **Real Web Search**: Perform actual web searches via DuckDuckGo and return real results
- **Advanced Anti-Detection**: Built-in anti-detection measures to avoid bot blocking
  - Automatic image blocking to appear more like a real user
  - Anti-detection Chrome arguments to prevent automation detection
  - Randomized sleep intervals to mimic human behavior
  - Cloudflare bypass capabilities
- **Auto-Retry Functionality**: Automatic retry mechanism with configurable attempts and delays
- **Page Content Extraction**: Visit webpages and extract content as plain text
- **Automatic Content Chunking**: Content is automatically split into 5000-character chunks
- **Load More Functionality**: Load next content chunks automatically without parameters
- **Search on Page**: Search for text within page content with context snippets
- **Search Next on Page**: Continue previous searches automatically
- **Read Specific Chunk**: Read content of specific chunks by index
- **Social Media Scraping**: Extract information from social media profiles
- **News Article Extraction**: Get content from news articles with metadata
- **E-commerce Product Data**: Extract product details from online stores
- **Business Information**: Gather business details from directory sites
- **Document Download**: Download and extract content from documents

## Installation

1. Install the required dependencies:
```bash
pip install botasaurus
```

## Configuration for AI Agents (Claude Desktop)

To use this MCP server with AI agents like Claude Desktop, you need to configure the `claude_desktop_config.json` file.

### Step 1: Locate the Configuration File

The configuration file is located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Configure the Botasaurus Server

Add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "botasaurus-web-search": {
      "command": "python",
      "args": [
        "/path/to/your/botasaurus-web-search/botasaurus_mcp_server.py"
      ]
    }
  }
}
```

Replace `/path/to/your/botasaurus-web-search/botasaurus_mcp_server.py` with the absolute path to your `botasaurus_mcp_server.py` file.

### Alternative Configuration with uv (Recommended)

If you're using `uv` as your Python package manager:

```json
{
  "mcpServers": {
    "botasaurus-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/botasaurus-web-search",
        "run",
        "botasaurus_mcp_server.py"
      ]
    }
  }
}
```

### Step 3: Restart Claude Desktop

After saving the configuration file, completely quit and restart Claude Desktop for the changes to take effect. You should now see the Botasaurus tools available in Claude Desktop.

## Usage

The server can be run as an MCP endpoint that AI applications can connect to. It provides the following tools:

### Web Search
```json
{
  "name": "botasaurus_search",
  "arguments": {
    "query": "Python programming tutorials",
    "max_results": 10
  }
}
```

### Visit Page
```json
{
  "name": "visit_page",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### Load More (Automatic)
```json
{
  "name": "load_more",
  "arguments": {}
}
```

### Search on Page
```json
{
  "name": "search_on_page",
  "arguments": {
    "text": "search term",
    "num_snippets": 5
  }
}
```

### Search Next on Page
```json
{
  "name": "search_next_on_page",
  "arguments": {
    "num_snippets": 3
  }
}
```

### Read Chunk
```json
{
  "name": "read_chunk",
  "arguments": {
    "chunk_index": 0
  }
}
```

## Content Chunking

The server automatically chunks page content into 5000-character segments:
- `visit_page` returns "Chunk 0\n{content}..." (first chunk with prefix) - always extracts as text
- `load_more` returns next chunks automatically without any parameters
- `read_chunk` allows reading specific chunks by index
- Search tools work across all chunks automatically

## Security

- URL validation prevents access to local resources
- Rate limiting prevents abuse
- Input sanitization for all parameters
- Session timeouts for browser instances
- Safe content extraction with proper validation

## Architecture

The server implements the MCP protocol with:
- JSON-RPC 2.0 communication
- Session management for continued browser interactions
- Botasaurus integration for robust web scraping
- Input validation and security checks
- Automatic content chunking and context management
- Real-time search capabilities within page content

## Documentation

For detailed documentation, see the [docs](docs/index.md) folder.

## Testing

Run the test suite:
```bash
python tests/run_all_tests.py
```

The test suite includes:
- Web search functionality tests
- Content chunking tests
- Search functionality tests
- Integration tests
- Real functionality verification tests