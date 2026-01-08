# Botasaurus MCP Server Documentation

Welcome to the Botasaurus MCP Server documentation. This Model Context Protocol (MCP) server provides AI applications with powerful web scraping capabilities.

## Table of Contents

- [Overview](index.md) - General overview of the Botasaurus MCP Server
- [Installation Guide](installation.md) - Step-by-step installation instructions
- [API Reference](api-reference.md) - Complete API reference for all tools
- [Usage Examples](usage-examples.md) - Practical examples and workflows

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install botasaurus
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```

3. **Connect with an MCP client** to access the web scraping tools.

## Available Tools

- `botasaurus_search` - Real web searches via DuckDuckGo
- `visit_page` - Page content extraction with automatic chunking
- `load_more` - Load next content chunks automatically
- `search_on_page` - Search for text within page content
- `search_next_on_page` - Continue previous searches
- `read_chunk` - Read specific chunks by index
- Social media, news, product, and business information scraping tools

## Support

For support, please check the documentation or create an issue in the repository.