# Usage Examples

## Basic Web Search

```json
{
  "name": "web_search",
  "arguments": {
    "query": "artificial intelligence trends 2025",
    "max_results": 5
  }
}
```

## Content Extraction and Navigation

### Step 1: Visit a page
```json
{
  "name": "visit_page",
  "arguments": {
    "url": "https://example.com/article"
  }
}
```

### Step 2: Load more content (automatic)
```json
{
  "name": "load_more",
  "arguments": {}
}
```

### Step 3: Read specific chunk
```json
{
  "name": "read_chunk",
  "arguments": {
    "chunk_index": 2
  }
}
```

## Content Search

### Step 1: Search for text on page
```json
{
  "name": "search_on_page",
  "arguments": {
    "text": "machine learning",
    "num_snippets": 3
  }
}
```

### Step 2: Continue search for more results
```json
{
  "name": "search_next_on_page",
  "arguments": {
    "num_snippets": 2
  }
}
```

## Complete Workflow Example

Here's a complete example of how to use the tools in sequence:

1. **Search for relevant pages:**
```json
{
  "name": "web_search",
  "arguments": {
    "query": "Python web scraping tutorial",
    "max_results": 3
  }
}
```

2. **Visit the most relevant page:**
```json
{
  "name": "visit_page",
  "arguments": {
    "url": "https://example.com/python-scraping-tutorial"
  }
}
```

3. **Search for specific information in the content:**
```json
{
  "name": "search_on_page",
  "arguments": {
    "text": "BeautifulSoup",
    "num_snippets": 5
  }
}
```

4. **Get more search results if needed:**
```json
{
  "name": "search_next_on_page",
  "arguments": {
    "num_snippets": 3
  }
}
```

5. **Load more content if available:**
```json
{
  "name": "load_more",
  "arguments": {}
}
```

6. **Read a specific chunk if needed:**
```json
{
  "name": "read_chunk",
  "arguments": {
    "chunk_index": 1
  }
}
```

## Advanced Search Example

To find specific information across a long document:

1. **Visit the document:**
```json
{
  "name": "visit_page",
  "arguments": {
    "url": "https://example.com/technical-documentation"
  }
}
```

2. **Search for key terms:**
```json
{
  "name": "search_on_page",
  "arguments": {
    "text": "API endpoint",
    "num_snippets": 4
  }
}
```

3. **Continue searching for more occurrences:**
```json
{
  "name": "search_next_on_page",
  "arguments": {
    "num_snippets": 4
  }
}
```

4. **Read specific sections of interest:**
```json
{
  "name": "read_chunk",
  "arguments": {
    "chunk_index": 3
  }
}
```

## Error Handling

The tools return error objects when issues occur:

```json
{
  "error": "No active session found. Please call visit_page first."
}
```

Common errors:
- `No active session found` - Call `visit_page` first
- `No content chunks available` - Page content is not chunked
- `Chunk index X is out of range` - Invalid chunk index provided
- `No active search context found` - Call `search_on_page` before `search_next_on_page`