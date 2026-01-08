#!/usr/bin/env python3
"""
Botasaurus MCP Server - Web Scraping Tools for AI

This MCP server provides AI applications with powerful web scraping capabilities
through standardized tools using the Model Context Protocol.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import re
from urllib.parse import urlparse

from botasaurus.browser import browser, Driver
from botasaurus.request import request, Request
from botasaurus.soupify import soupify
from botasaurus.cache import DontCache

import mcp
from mcp.server.fastmcp.server import FastMCP
from mcp import types


# Global context to track the current session across calls
_current_session_context = {}

# Global context to track search parameters for search_next_on_page
_current_search_context = {}

class SessionManager:
    """Manages browser sessions for tools that require continuity like load_more"""

    def __init__(self, session_timeout_minutes=30):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

    def create_session(self, driver: Driver) -> str:
        """Create a new session with the given driver"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'driver': driver,
            'created_at': datetime.now(),
            'last_used': datetime.now()
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID, cleaning up expired sessions"""
        self._cleanup_expired_sessions()

        session = self.sessions.get(session_id)
        if session:
            session['last_used'] = datetime.now()
        return session

    def remove_session(self, session_id: str):
        """Remove a session"""
        if session_id in self.sessions:
            # Close the driver if it exists
            session = self.sessions[session_id]
            if 'driver' in session and session['driver']:
                try:
                    session['driver'].quit()
                except:
                    pass
            del self.sessions[session_id]

    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if now - session['last_used'] > self.session_timeout
        ]
        for sid in expired_sessions:
            self.remove_session(sid)


# Create the FastMCP server instance
mcp = FastMCP(
    name="Botasaurus MCP Server",
    instructions="""You have access to web scraping tools that can search the web, visit pages, and extract content. Here's how to use them effectively:

WEB SEARCH: Use botasaurus_search to find information and URLs when you don't have specific links. Always start with this tool if you need to find new information.

VISIT PAGES: Use visit_page to extract content from URLs. The content comes as text in chunks of up to 5000 characters. Always use visit_page after getting URLs from botasaurus_search.

LOAD MORE: If visit_page returns 'has_more_chunks': true, use load_more to get additional content. Continue until has_more_chunks becomes false.

SEARCH ON PAGE: After visiting a page, use search_on_page to find specific information within the content. Use search_next_on_page to get more results for the same search.

READ CHUNK: Use read_chunk to access specific content chunks by index if needed.

SPECIALIZED TOOLS: For specific content types, use:
- extract_news_article: For news articles
- scrape_social_profile: For social media profiles
- scrape_product: For product information

WORKFLOW EXAMPLES:
- To research a topic: botasaurus_search → visit_page → search_on_page
- To read a long article: visit_page → check has_more_chunks → load_more if needed
- To find specific info: visit_page → search_on_page → search_next_on_page if needed"""
)

session_manager = SessionManager()


def validate_url(url: str) -> bool:
    """Validate that a URL is safe to access"""
    try:
        parsed = urlparse(url)
        # Block file:// and other potentially unsafe schemes
        if parsed.scheme not in ['http', 'https']:
            return False
        # Block localhost and private IPs for security
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
        if parsed.hostname and parsed.hostname.startswith('192.168.'):
            return False
        if parsed.hostname and parsed.hostname.startswith('10.'):
            return False
        if parsed.hostname and parsed.hostname.startswith('172.'):
            return False
        return True
    except:
        return False


async def _web_search_impl(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Internal implementation of web search using DuckDuckGo"""
    if not query or query.strip() == "":
        return {
            "query": query,
            "results": [],
            "total_results": 0
        }

    try:
        from ddgs import DDGS

        ddgs = DDGS()
        search_results = list(ddgs.text(query, max_results=max_results))

        results = []
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        # If DuckDuckGo search fails, return an error
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "error": f"Search failed: {str(e)}"
        }


@mcp.tool(
    name="botasaurus_search",
    title="Botasaurus Search",
    description="Perform web searches and return structured results from the internet. Use this tool when you need to find current information, research topics, or discover URLs related to a specific query. The tool uses DuckDuckGo search engine to provide unbiased results with titles, URLs, and snippets. Ideal for initial research, fact-checking, or finding resources on a topic.",
)
async def botasaurus_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Perform a web search (simulated - in a real implementation, this would use a search API)"""
    return await _web_search_impl(query, max_results)


def _visit_page_impl(url: str) -> Dict[str, Any]:
    """Internal implementation of visit page - always extracts content as text format"""

    @browser(headless=True)
    def _visit_page_internal(driver: Driver, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal task to visit a page and extract content as text"""
        url = data["url"]

        if not validate_url(url):
            return {"error": f"Invalid or unsafe URL: {url}"}

        try:
            driver.get(url)

            # Wait a bit for the page to load
            driver.sleep(2)

            # Extract content as text (always use text format)
            content = driver.get_text("body")

            # Create a session for potential load_more functionality
            session_id = session_manager.create_session(driver)

            # Store the full content in the session and return first chunk
            session = session_manager.get_session(session_id)
            if session:
                # Split content into chunks for load_more functionality
                if isinstance(content, str):
                    # For text content, split into chunks of ~5000 characters
                    chunk_size = 5000
                    content_chunks = []
                    for i in range(0, len(content), chunk_size):
                        content_chunks.append(content[i:i+chunk_size])

                    session['content_chunks'] = content_chunks
                    session['current_chunk_index'] = 0

                    # Format the first chunk with "Chunk 0" prefix and "..." suffix
                    if content_chunks:
                        chunk_index = 0
                        chunked_content = f"Chunk {chunk_index}\n{content_chunks[chunk_index]}"
                        if len(content_chunks[chunk_index]) == chunk_size:  # If chunk is full size, add ...
                            chunked_content += "..."
                    else:
                        chunked_content = "Chunk 0\n"
                else:
                    # For non-string content, return as-is and don't chunk
                    session['content_chunks'] = [content]
                    session['current_chunk_index'] = 0
                    chunked_content = content

            # Set this session as the current context for automatic load_more
            _current_session_context['current'] = session_id

            return {
                "url": url,
                "content": chunked_content,
                "format": "text",  # Always return "text" format
                "chunk_index": 0,
                "has_more_chunks": len(session['content_chunks']) > 1 if session else False
            }

        except Exception as e:
            # Clean up the driver if an error occurs
            try:
                driver.quit()
            except:
                pass
            return {"error": f"Failed to visit page: {str(e)}"}

    # Call the internal function with the task data
    task_data = {
        "url": url
    }
    return _visit_page_internal(task_data)


@mcp.tool(
    name="visit_page",
    title="Visit and Extract Page Content",
    description="Visit a webpage and extract its content as plain text. Use this tool when you need to read the content of a specific URL that was found through botasaurus_search or provided directly. The tool extracts content as plain text and automatically chunks large pages for efficient processing. The content is automatically chunked for large pages, allowing you to load more content later using the load_more tool.",
)
def visit_page(url: str) -> Dict[str, Any]:
    """Task to visit a page and extract content as text"""
    return _visit_page_impl(url)


def _load_more_impl() -> Dict[str, Any]:
    """Internal implementation of load more - automatically gets session from context"""
    # Get the current session from global context
    current_session_id = _current_session_context.get('current')
    if not current_session_id:
        return {"error": "No active session found. Please call visit_page first."}

    session = session_manager.get_session(current_session_id)
    if not session:
        return {"error": f"Session not found: {current_session_id}"}

    try:
        # Check if we have content chunks to serve (for text-based pagination)
        if 'content_chunks' in session:
            current_index = session.get('current_chunk_index', 0)
            next_index = current_index + 1

            if next_index < len(session['content_chunks']):
                # Return next chunk from stored content
                session['current_chunk_index'] = next_index
                raw_chunk = session['content_chunks'][next_index]

                # Format the chunk with "Chunk X" prefix and "..." suffix
                formatted_content = f"Chunk {next_index}\n{raw_chunk}"
                if len(raw_chunk) == 5000:  # If chunk is full size, add ...
                    formatted_content += "..."

                return {
                    "status": "success",
                    "message": f"Chunk {next_index} loaded successfully",
                    "content": formatted_content,
                    "chunk_index": next_index,
                    "has_more_chunks": next_index < len(session['content_chunks']) - 1
                }
            else:
                # No more chunks available
                return {
                    "status": "complete",
                    "message": "No more chunks available",
                    "chunk_index": current_index,
                    "has_more_chunks": False
                }

        # If no stored content chunks, return error
        return {
            "status": "error",
            "message": "No content chunks available for this session"
        }

    except Exception as e:
        return {"error": f"Failed to load more content: {str(e)}"}


@mcp.tool(
    name="load_more",
    title="Load More Content",
    description="Load the next content chunk from the currently visited page. Use this tool after calling visit_page when the 'has_more_chunks' field in the response is True, indicating that the page content was too large and has been split into multiple chunks. This tool requires no parameters and automatically continues from where the previous visit_page or load_more call left off. Use this to read the complete content of large web pages.",
)
def load_more() -> Dict[str, Any]:
    """Load more content automatically from the current page session - no inputs required"""
    return _load_more_impl()


def _search_on_page_impl(text: str, num_snippets: int = 5) -> Dict[str, Any]:
    """Internal implementation of search on page - searches for text in the current session content"""
    # Get the current session from global context
    current_session_id = _current_session_context.get('current')
    if not current_session_id:
        return {"error": "No active session found. Please call visit_page first."}

    session = session_manager.get_session(current_session_id)
    if not session:
        return {"error": f"Session not found: {current_session_id}"}

    try:
        # Check if we have content chunks to search in
        if 'content_chunks' in session:
            content_chunks = session['content_chunks']
            all_chunks_text = "".join(content_chunks)

            # Search for the text in the content
            import re
            # Find all occurrences of the text (case insensitive)
            matches = []
            text_lower = text.lower()
            all_text_lower = all_chunks_text.lower()

            start = 0
            while True:
                pos = all_text_lower.find(text_lower, start)
                if pos == -1:
                    break
                matches.append(pos)
                start = pos + 1

                if len(matches) >= num_snippets * 10:  # Find more than needed to have options
                    break

            # Create snippets around each match
            snippets = []
            snippet_length = 200  # Length of context around each match
            for match_pos in matches[:num_snippets]:
                start_pos = max(0, match_pos - snippet_length // 2)
                end_pos = min(len(all_chunks_text), match_pos + len(text) + snippet_length // 2)

                # Extract the snippet
                snippet = all_chunks_text[start_pos:end_pos]

                # Find the exact match position in the snippet
                match_in_snippet = snippet.lower().find(text_lower)
                if match_in_snippet != -1:
                    # Highlight the found text by adding context
                    before = snippet[:match_in_snippet]
                    found_text = snippet[match_in_snippet:match_in_snippet + len(text)]
                    after = snippet[match_in_snippet + len(text):]

                    # Add context markers
                    snippet_text = f"...{before}[{found_text}]{after}..."

                    # Determine which chunk this match belongs to
                    chunk_index = 0
                    temp_pos = 0
                    for i, chunk in enumerate(content_chunks):
                        if temp_pos <= match_pos < temp_pos + len(chunk):
                            chunk_index = i
                            break
                        temp_pos += len(chunk)

                    snippets.append({
                        "chunk_index": chunk_index,
                        "snippet": snippet_text.strip(),
                        "position": match_pos
                    })

                    if len(snippets) >= num_snippets:
                        break

            # Store search context for search_next_on_page
            _current_search_context.update({
                'session_id': current_session_id,
                'search_text': text,
                'all_matches': matches,
                'current_index': len(snippets),
                'num_snippets': num_snippets
            })

            return {
                "search_text": text,
                "total_matches": len(matches),
                "snippets_returned": len(snippets),
                "snippets": snippets
            }
        else:
            return {
                "search_text": text,
                "total_matches": 0,
                "snippets_returned": 0,
                "snippets": [],
                "message": "No content chunks available for searching in this session"
            }

    except Exception as e:
        return {"error": f"Failed to search on page: {str(e)}"}


def _search_next_on_page_impl(num_snippets: int = 5) -> Dict[str, Any]:
    """Internal implementation of search next on page - continues search from previous search"""
    # Get the current search context
    if not _current_search_context:
        return {"error": "No active search context found. Please call search_on_page first."}

    search_text = _current_search_context.get('search_text')
    all_matches = _current_search_context.get('all_matches', [])
    current_index = _current_search_context.get('current_index', 0)
    session_id = _current_search_context.get('session_id')

    if not search_text:
        return {"error": "No search text found in context."}

    if not session_id:
        return {"error": "No session ID found in context."}

    session = session_manager.get_session(session_id)
    if not session:
        return {"error": f"Session not found: {session_id}"}

    try:
        # Check if we have content chunks to search in
        if 'content_chunks' in session:
            content_chunks = session['content_chunks']
            all_chunks_text = "".join(content_chunks)

            # Get more snippets starting from current index
            snippets = []
            snippet_length = 200  # Length of context around each match
            text_lower = search_text.lower()

            for i in range(current_index, min(current_index + num_snippets, len(all_matches))):
                match_pos = all_matches[i]

                start_pos = max(0, match_pos - snippet_length // 2)
                end_pos = min(len(all_chunks_text), match_pos + len(search_text) + snippet_length // 2)

                # Extract the snippet
                snippet = all_chunks_text[start_pos:end_pos]

                # Find the exact match position in the snippet
                match_in_snippet = snippet.lower().find(text_lower)
                if match_in_snippet != -1:
                    # Highlight the found text by adding context
                    before = snippet[:match_in_snippet]
                    found_text = snippet[match_in_snippet:match_in_snippet + len(search_text)]
                    after = snippet[match_in_snippet + len(search_text):]

                    # Add context markers
                    snippet_text = f"...{before}[{found_text}]{after}..."

                    # Determine which chunk this match belongs to
                    chunk_index = 0
                    temp_pos = 0
                    for j, chunk in enumerate(content_chunks):
                        if temp_pos <= match_pos < temp_pos + len(chunk):
                            chunk_index = j
                            break
                        temp_pos += len(chunk)

                    snippets.append({
                        "chunk_index": chunk_index,
                        "snippet": snippet_text.strip(),
                        "position": match_pos
                    })

            # Update the search context
            _current_search_context['current_index'] = min(current_index + num_snippets, len(all_matches))

            return {
                "search_text": search_text,
                "total_matches": len(all_matches),
                "snippets_returned": len(snippets),
                "snippets": snippets,
                "has_more_results": len(all_matches) > _current_search_context['current_index']
            }
        else:
            return {
                "search_text": search_text,
                "total_matches": 0,
                "snippets_returned": 0,
                "snippets": [],
                "message": "No content chunks available for searching in this session"
            }

    except Exception as e:
        return {"error": f"Failed to search next on page: {str(e)}"}


def _read_chunk_impl(chunk_index: int) -> Dict[str, Any]:
    """Internal implementation of read chunk - returns content of a specific chunk"""
    # Get the current session from global context
    current_session_id = _current_session_context.get('current')
    if not current_session_id:
        return {"error": "No active session found. Please call visit_page first."}

    session = session_manager.get_session(current_session_id)
    if not session:
        return {"error": f"Session not found: {current_session_id}"}

    try:
        # Check if we have content chunks available
        if 'content_chunks' in session:
            content_chunks = session['content_chunks']

            if chunk_index < 0 or chunk_index >= len(content_chunks):
                return {
                    "session_id": current_session_id,
                    "chunk_index": chunk_index,
                    "error": f"Chunk index {chunk_index} is out of range. Available chunks: 0 to {len(content_chunks)-1}",
                    "total_chunks": len(content_chunks)
                }

            chunk_content = content_chunks[chunk_index]

            return {
                "chunk_index": chunk_index,
                "content": chunk_content,
                "total_chunks": len(content_chunks),
                "chunk_size": len(chunk_content)
            }
        else:
            return {
                "chunk_index": chunk_index,
                "error": "No content chunks available in this session",
                "total_chunks": 0
            }

    except Exception as e:
        return {"error": f"Failed to read chunk: {str(e)}"}


@mcp.tool(
    name="search_on_page",
    title="Search on Page",
    description="Search for specific text within the currently visited page content. Use this tool when you've loaded a page with visit_page and need to find specific information within that content. The tool returns context snippets around each match, making it easy to locate relevant information. Specify how many snippets you want with the num_snippets parameter. This is particularly useful for finding specific sections in long articles, documentation, or research papers without manually scanning through all content.",
)
def search_on_page(text: str, num_snippets: int = 5) -> Dict[str, Any]:
    """Search for text within the currently visited page content"""
    return _search_on_page_impl(text, num_snippets)


@mcp.tool(
    name="search_next_on_page",
    title="Search Next on Page",
    description="Continue searching for the same text from the previous search_on_page call. Use this tool when the initial search_on_page returned fewer results than expected or when you need to find additional occurrences of the same term. This tool picks up where the previous search left off and returns the next set of matching snippets. It's useful for thoroughly searching through long documents or when you need to find all instances of particular information.",
)
def search_next_on_page(num_snippets: int = 5) -> Dict[str, Any]:
    """Continue searching for the same text from the previous search_on_page call"""
    return _search_next_on_page_impl(num_snippets)


@mcp.tool(
    name="read_chunk",
    title="Read Specific Chunk",
    description="Read the content of a specific chunk from the currently visited page. Use this tool when you need to access a particular section of a large page that has been split into multiple chunks. You must specify the chunk_index to retrieve. This tool is useful when you know exactly which part of the content you need or when navigating through large documents in a non-linear fashion. The total number of chunks is available in the response from visit_page or load_more.",
)
def read_chunk(chunk_index: int) -> Dict[str, Any]:
    """Read the content of a specific chunk from the current page session"""
    return _read_chunk_impl(chunk_index)


def _scrape_social_profile_impl(platform: str, profile_url: str) -> Dict[str, Any]:
    """Internal implementation of scrape social profile"""

    @browser(headless=True)
    def _scrape_social_internal(driver: Driver, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal task to scrape social media profile information"""
        profile_url = data["profile_url"]
        platform = data["platform"]

        if not validate_url(profile_url):
            return {"error": f"Invalid or unsafe URL: {profile_url}"}

        try:
            driver.get(profile_url)
            driver.sleep(3)  # Wait for page to load

            # Extract common profile elements (this would be customized per platform)
            profile_data = {
                "platform": platform,
                "url": profile_url,
                "title": driver.get_text("title"),
            }

            # Try to find common profile elements
            possible_name_selectors = [
                "[data-testid='ocf-headline']",  # Twitter
                ".profile h1",  # Generic
                "h1",  # Generic
                ".username",  # Generic
                "[data-testid='UserProfileHeader_Items']"  # Twitter
            ]

            for selector in possible_name_selectors:
                try:
                    name = driver.get_text(selector)
                    if name and len(name.strip()) > 0:
                        profile_data["name"] = name.strip()
                        break
                except:
                    continue

            # Try to find bio/description
            possible_bio_selectors = [
                ".bio",  # Generic
                "[data-testid='UserProfileHeader_Items']",  # Twitter
                ".profile p",  # Generic
                ".description"  # Generic
            ]

            for selector in possible_bio_selectors:
                try:
                    bio = driver.get_text(selector)
                    if bio and len(bio.strip()) > 0:
                        profile_data["bio"] = bio.strip()
                        break
                except:
                    continue

            return profile_data

        except Exception as e:
            return {"error": f"Failed to scrape profile: {str(e)}"}

    # Call the internal function with the task data
    task_data = {
        "profile_url": profile_url,
        "platform": platform
    }
    return _scrape_social_internal(task_data)


@mcp.tool(
    name="scrape_social_profile",
    title="Scrape Social Media Profile",
    description="Extract public information from social media profiles. Use this tool when you need to gather publicly available information from social media platforms like Twitter, LinkedIn, Instagram, etc. You need to provide both the platform name and the profile URL. The tool attempts to extract profile names, bios, and other public information. This is useful for research, background checks, or gathering contact information from professional networks. Note that only publicly accessible information is retrieved, respecting privacy settings.",
)
def scrape_social_profile(platform: str, profile_url: str) -> Dict[str, Any]:
    """Scrape social media profile information"""
    return _scrape_social_profile_impl(platform, profile_url)


def _extract_news_article_impl(article_url: str, include_metadata: bool = True) -> Dict[str, Any]:
    """Internal implementation of extract news article"""

    @request
    def _extract_news_internal(request_obj: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal task to extract content from a news article"""
        article_url = data["article_url"]
        include_metadata = data.get("include_metadata", True)

        if not validate_url(article_url):
            return {"error": f"Invalid or unsafe URL: {article_url}"}

        try:
            response = request_obj.get(article_url)
            soup = soupify(response)

            # Extract article content
            article_data = {
                "url": article_url,
                "title": "",
                "content": "",
                "author": "",
                "date": "",
            }

            # Extract title
            title_selectors = ["h1", "h2", "title", ".article-title", ".post-title"]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    article_data["title"] = title_elem.get_text().strip()
                    break

            # Extract main content
            content_selectors = [
                ".article-body", ".post-content", ".entry-content",
                ".content", "article", ".story-body", ".article-content"
            ]
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    article_data["content"] = content_elem.get_text().strip()
                    break

            # If no specific content selector worked, get all paragraphs
            if not article_data["content"]:
                paragraphs = soup.select("p")
                article_data["content"] = " ".join([p.get_text().strip() for p in paragraphs])

            # Extract metadata if requested
            if include_metadata:
                # Extract author
                author_selectors = [
                    ".author", ".byline", "[rel='author']",
                    ".article-author", ".post-author"
                ]
                for selector in author_selectors:
                    author_elem = soup.select_one(selector)
                    if author_elem:
                        article_data["author"] = author_elem.get_text().strip()
                        break

                # Extract date
                date_selectors = [
                    "time", ".date", ".publish-date",
                    ".article-date", "[property*='published']"
                ]
                for selector in date_selectors:
                    date_elem = soup.select_one(selector)
                    if date_elem:
                        date_text = date_elem.get_text().strip()
                        if date_text:
                            article_data["date"] = date_text
                            break

            return article_data

        except Exception as e:
            return {"error": f"Failed to extract article: {str(e)}"}

    # Call the internal function with the task data
    task_data = {
        "article_url": article_url,
        "include_metadata": include_metadata
    }
    return _extract_news_internal(task_data)


@mcp.tool(
    name="extract_news_article",
    title="Extract News Article",
    description="Extract full content from news articles with metadata. Use this tool when you need to get the complete text of a news article, blog post, or other journalistic content from a URL. The tool retrieves the main content along with important metadata like title, author, and publication date. You can control whether to include metadata with the include_metadata parameter. This is ideal for reading full articles found through web_search, getting detailed information from news sources, or extracting content from blog posts for analysis.",
)
def extract_news_article(article_url: str, include_metadata: bool = True) -> Dict[str, Any]:
    """Extract content from a news article"""
    return _extract_news_article_impl(article_url, include_metadata)


def _scrape_product_impl(product_url: str, include_reviews: bool = False) -> Dict[str, Any]:
    """Internal implementation of scrape product"""

    @browser(headless=True)
    def _scrape_product_internal(driver: Driver, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal task to scrape product information from e-commerce sites"""
        product_url = data["product_url"]
        include_reviews = data.get("include_reviews", False)

        if not validate_url(product_url):
            return {"error": f"Invalid or unsafe URL: {product_url}"}

        try:
            driver.get(product_url)
            driver.sleep(3)  # Wait for page to load

            product_data = {
                "url": product_url,
                "name": "",
                "price": "",
                "description": "",
                "availability": "",
                "reviews": [] if include_reviews else "Reviews available but not included (set include_reviews=True)"
            }

            # Extract product name
            name_selectors = [
                "[data-testid='product-title']",
                ".product-title",
                ".product-name",
                "h1",
                "[data-testid='title']",
                ".title"
            ]

            for selector in name_selectors:
                try:
                    name = driver.get_text(selector)
                    if name and len(name.strip()) > 0:
                        product_data["name"] = name.strip()
                        break
                except:
                    continue

            # Extract price
            price_selectors = [
                "[data-testid='price']",
                ".price",
                ".product-price",
                ".current-price",
                "[class*='price']"
            ]

            for selector in price_selectors:
                try:
                    price = driver.get_text(selector)
                    if price and len(price.strip()) > 0:
                        product_data["price"] = price.strip()
                        break
                except:
                    continue

            # Extract description
            desc_selectors = [
                ".product-description",
                ".description",
                ".product-details",
                "[data-testid='description']"
            ]

            for selector in desc_selectors:
                try:
                    desc = driver.get_text(selector)
                    if desc and len(desc.strip()) > 0:
                        product_data["description"] = desc.strip()
                        break
                except:
                    continue

            # Extract availability
            avail_selectors = [
                ".availability",
                ".stock",
                ".in-stock",
                "[data-testid*='stock']"
            ]

            for selector in avail_selectors:
                try:
                    avail = driver.get_text(selector)
                    if avail and len(avail.strip()) > 0:
                        product_data["availability"] = avail.strip()
                        break
                except:
                    continue

            # Extract reviews if requested
            if include_reviews:
                review_selectors = [
                    ".review",
                    ".review-item",
                    "[data-testid*='review']",
                    ".customer-review"
                ]

                try:
                    review_elements = driver.find_elements(review_selectors[0])
                    reviews = []
                    for review_elem in review_elements[:5]:  # Limit to first 5 reviews
                        try:
                            review_text = review_elem.text
                            if review_text and len(review_text.strip()) > 0:
                                reviews.append(review_text.strip())
                        except:
                            continue
                    product_data["reviews"] = reviews
                except:
                    product_data["reviews"] = "Could not extract reviews"

            return product_data

        except Exception as e:
            return {"error": f"Failed to scrape product: {str(e)}"}

    # Call the internal function with the task data
    task_data = {
        "product_url": product_url,
        "include_reviews": include_reviews
    }
    return _scrape_product_internal(task_data)


@mcp.tool(
    name="scrape_product",
    title="Scrape Product Information",
    description="Extract product details like price, description, reviews from e-commerce sites. Use this tool when you need to gather information about products from online stores like Amazon, eBay, or other e-commerce platforms. You can optionally include reviews by setting include_reviews to True. The tool attempts to extract product name, price, description, availability status, and other relevant details. This is useful for price comparison, product research, market analysis, or gathering product specifications. Note that some sites may have anti-scraping measures that could limit data availability.",
)
def scrape_product(product_url: str, include_reviews: bool = False) -> Dict[str, Any]:
    """Scrape product information from e-commerce sites"""
    return _scrape_product_impl(product_url, include_reviews)


async def _scrape_business_info_impl(search_query: str, location: str = "") -> Dict[str, Any]:
    """Internal implementation of scrape business info (simulated)"""
    return {
        "error": "scrape_business_info is not fully implemented in this demo",
        "query": search_query,
        "location": location
    }


@mcp.tool(
    name="scrape_business_info",
    title="Scrape Business Information",
    description="Extract business details like address, phone, hours, services",
)
async def scrape_business_info(search_query: str, location: str = "") -> Dict[str, Any]:
    """Scrape business information (simulated)"""
    return await _scrape_business_info_impl(search_query, location)


async def _monitor_webpage_impl(url: str, selector: str = "", frequency_minutes: int = 60) -> Dict[str, Any]:
    """Internal implementation of monitor webpage (simulated)"""
    return {
        "error": "monitor_webpage is not fully implemented in this demo",
        "url": url,
        "selector": selector,
        "frequency_minutes": frequency_minutes
    }


@mcp.tool(
    name="monitor_webpage",
    title="Monitor Webpage for Changes",
    description="Monitor a webpage and detect when content changes",
)
async def monitor_webpage(url: str, selector: str = "", frequency_minutes: int = 60) -> Dict[str, Any]:
    """Monitor webpage for changes (simulated)"""
    return await _monitor_webpage_impl(url, selector, frequency_minutes)


async def _download_document_impl(document_url: str, extract_text: bool = True) -> Dict[str, Any]:
    """Internal implementation of download document (simulated)"""
    return {
        "error": "download_document is not fully implemented in this demo",
        "document_url": document_url,
        "extract_text": extract_text
    }


@mcp.tool(
    name="download_document",
    title="Download and Extract Document Content",
    description="Download documents from web pages and extract their text content",
)
async def download_document(document_url: str, extract_text: bool = True) -> Dict[str, Any]:
    """Download and extract document content (simulated)"""
    return await _download_document_impl(document_url, extract_text)


if __name__ == "__main__":
    mcp.run(transport="stdio")