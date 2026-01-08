# Botasaurus MCP Server Documentation

## Overview

The Botasaurus MCP Server is a Model Context Protocol (MCP) server that provides AI applications with powerful web scraping capabilities using the Botasaurus framework.

## Features

- **Web Search Tool**: Perform web searches and return structured results
- **Page Content Extraction**: Visit webpages and extract content as plain text
- **Content Chunking**: Automatic content chunking with 5000 character chunks
- **Load More Functionality**: Continue interacting with pages to load additional content automatically
- **Search on Page**: Search for text within page content with context snippets
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

## Architecture

The server implements the MCP protocol with:
- JSON-RPC 2.0 communication
- Session management for continued browser interactions
- Botasaurus integration for robust web scraping
- Input validation and security checks
- Automatic content chunking and context management
- Real-time search capabilities within page content

## Security

- URL validation prevents access to local resources
- Rate limiting prevents abuse
- Input sanitization for all parameters
- Session timeouts for browser instances
- Safe content extraction with proper validation

## Tools Reference

### botasaurus_search
- **Description**: Perform web searches and return structured results
- **Arguments**:
  - `query` (string): The search query
  - `max_results` (int, optional): Maximum number of results (default: 10)

### visit_page
- **Description**: Visit a webpage and extract content as plain text
- **Arguments**:
  - `url` (string): The URL to visit

### load_more
- **Description**: Load the next content chunk automatically from the current page session
- **Arguments**: None required
- **Returns**: Next chunk of content with "Chunk X" prefix

### search_on_page
- **Description**: Search for text within the currently visited page content
- **Arguments**:
  - `text` (string): Text to search for
  - `num_snippets` (int, optional): Number of snippets to return (default: 5)
- **Returns**: Matched snippets with context and highlighted text

### search_next_on_page
- **Description**: Continue searching for the same text from the previous search_on_page call
- **Arguments**:
  - `num_snippets` (int, optional): Number of snippets to return (default: 5)
- **Returns**: Additional matched snippets continuing from previous search

### read_chunk
- **Description**: Read the content of a specific chunk from the current page session
- **Arguments**:
  - `chunk_index` (int): Index of the chunk to read
- **Returns**: Full content of the specified chunk with metadata

## Content Chunking

The server automatically chunks page content into 5000 character segments:
- `visit_page` returns "Chunk 0" with content and "..." suffix if full - always extracts as text
- `load_more` automatically returns subsequent chunks without parameters
- `read_chunk` allows reading specific chunks by index
- Search tools work across all chunks automatically

## Session Management

All tools maintain session context automatically:
- Page content is chunked and stored per session
- Search context remembers previous search terms
- Chunk navigation maintains position across calls
- Session cleanup occurs automatically on timeout

## Configuration Examples

Here are common configuration examples for different environments:

### Standard Python Configuration
```json
{
  "mcpServers": {
    "botasaurus-web-search": {
      "command": "python",
      "args": [
        "/absolute/path/to/botasaurus_mcp_server.py"
      ]
    }
  }
}
```

### Using uv Package Manager
```json
{
  "mcpServers": {
    "botasaurus-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/botasaurus-web-search",
        "run",
        "botasaurus_mcp_server.py"
      ]
    }
  }
}
```

### Multiple MCP Servers Configuration
```json
{
  "mcpServers": {
    "botasaurus-web-search": {
      "command": "python",
      "args": [
        "/path/to/botasaurus_mcp_server.py"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Documents"
      ]
    }
  }
}
```