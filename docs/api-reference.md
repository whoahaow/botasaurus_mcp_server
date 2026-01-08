# API Reference

## Web Search Tool

### `web_search`
Perform web searches and return structured results.

**Arguments:**
- `query` (string): The search query to execute
- `max_results` (int, optional): Maximum number of results to return (default: 10)

**Returns:**
- `query` (string): The original search query
- `results` (array): Array of search result objects
  - `title` (string): Title of the search result
  - `url` (string): URL of the search result
  - `snippet` (string): Snippet/description of the search result
- `total_results` (int): Total number of results returned

## Page Content Extraction Tools

### `visit_page`
Visit a webpage and extract content as plain text.

**Arguments:**
- `url` (string): The URL to visit

**Returns:**
- `url` (string): The visited URL
- `content` (string): Extracted content (formatted as "Chunk 0\n{content}...")
- `format` (string): Extract format used (always "text")
- `chunk_index` (int): Current chunk index (0 for first chunk)
- `has_more_chunks` (boolean): Whether more chunks are available

### `load_more`
Load the next content chunk automatically from the current page session.

**Arguments:** None required

**Returns:**
- `status` (string): Status of the operation ("success", "complete", etc.)
- `message` (string): Status message
- `content` (string): Next chunk content (formatted as "Chunk X\n{content}...")
- `chunk_index` (int): Current chunk index
- `has_more_chunks` (boolean): Whether more chunks are available

### `read_chunk`
Read the content of a specific chunk from the current page session.

**Arguments:**
- `chunk_index` (int): Index of the chunk to read

**Returns:**
- `chunk_index` (int): Index of the chunk read
- `content` (string): Content of the specified chunk
- `total_chunks` (int): Total number of chunks available
- `chunk_size` (int): Size of the chunk in characters
- `error` (string, optional): Error message if operation failed

## Search Tools

### `search_on_page`
Search for text within the currently visited page content.

**Arguments:**
- `text` (string): Text to search for
- `num_snippets` (int, optional): Number of snippets to return (default: 5)

**Returns:**
- `search_text` (string): The text that was searched for
- `total_matches` (int): Total number of matches found
- `snippets_returned` (int): Number of snippets returned
- `snippets` (array): Array of snippet objects
  - `chunk_index` (int): Index of the chunk containing the match
  - `snippet` (string): Snippet with context and highlighted text in brackets [text]
  - `position` (int): Position of the match in the full content
- `message` (string, optional): Additional message if needed

### `search_next_on_page`
Continue searching for the same text from the previous search_on_page call.

**Arguments:**
- `num_snippets` (int, optional): Number of snippets to return (default: 5)

**Returns:**
- `search_text` (string): The text that was searched for
- `total_matches` (int): Total number of matches found
- `snippets_returned` (int): Number of snippets returned
- `snippets` (array): Array of snippet objects
  - `chunk_index` (int): Index of the chunk containing the match
  - `snippet` (string): Snippet with context and highlighted text in brackets [text]
  - `position` (int): Position of the match in the full content
- `has_more_results` (boolean): Whether more results are available
- `message` (string, optional): Additional message if needed

## Social Media and Data Extraction Tools

### `scrape_social_profile`
Extract information from social media profiles.

**Arguments:**
- `platform` (string): Social media platform (e.g., "twitter", "linkedin")
- `profile_url` (string): URL of the profile to scrape

**Returns:**
- Various profile information depending on the platform

### `extract_news_article`
Get content from news articles with metadata.

**Arguments:**
- `url` (string): URL of the news article

**Returns:**
- Article content with title, author, publication date, and content

### `scrape_product`
Extract product details from online stores.

**Arguments:**
- `url` (string): URL of the product page

**Returns:**
- Product information including name, price, description, availability, and reviews

## Session Management

All tools that require continued interaction maintain session context automatically:
- Page content is chunked and stored per session
- Search context remembers previous search terms
- Chunk navigation maintains position across calls
- Sessions are cleaned up automatically on timeout