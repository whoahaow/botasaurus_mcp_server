# Installation Guide

## Prerequisites

- Python 3.12 or higher
- pip package manager
- Claude Desktop (for AI agent integration)

## Installation Steps

1. Clone or download the repository:
```bash
git clone <repository-url>
cd botasaurus-web-search
```

2. Install the required dependencies:
```bash
pip install botasaurus
```

3. Install the project in development mode:
```bash
pip install -e .
```

## Dependencies

The project requires the following dependencies:
- `botasaurus>=4.0.97` - Web scraping framework
- `mcp[cli]>=1.25.0` - Model Context Protocol implementation
- `ddgs>=9.10.0` - DuckDuckGo search API

## Configuration for AI Agents (Claude Desktop)

To integrate this MCP server with Claude Desktop, you need to configure the `claude_desktop_config.json` file.

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
        "/absolute/path/to/botasaurus-web-search/botasaurus_mcp_server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/botasaurus-web-search/botasaurus_mcp_server.py` with the actual absolute path to your server file.

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

After saving the configuration file, completely quit and restart Claude Desktop for the changes to take effect. The Botasaurus tools will now be available within Claude Desktop.

## Verification

After installation, you can verify the installation by running:
```bash
python -c "import botasaurus_mcp_server; print('Installation successful')"
```

## Troubleshooting

If you encounter any issues during installation:

1. Make sure you have Python 3.12 or higher installed
2. Update pip: `pip install --upgrade pip`
3. If you have issues with the botasaurus package, try: `pip install --no-cache-dir botasaurus`
4. For MCP configuration issues, ensure Claude Desktop is restarted after configuration changes
5. Verify that the paths in your configuration file are correct and accessible