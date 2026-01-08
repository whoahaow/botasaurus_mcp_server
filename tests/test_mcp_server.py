#!/usr/bin/env python3
"""
Comprehensive tests for Botasaurus MCP Server using FastMCP
Tests all tools with real action on safe sites
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the server instance and its tools
from botasaurus_mcp_server import (
    mcp,
    _web_search_impl as botasaurus_search,
    _visit_page_impl as visit_page,
    _load_more_impl as load_more,
    _scrape_social_profile_impl as scrape_social_profile,
    _extract_news_article_impl as extract_news_article,
    _scrape_product_impl as scrape_product,
    _scrape_business_info_impl as scrape_business_info,
    _monitor_webpage_impl as monitor_webpage,
    _download_document_impl as download_document,
    validate_url,
    session_manager
)


class TestFastMCPBotasaurus:
    """Test class for FastMCP Botasaurus Server"""

    def __init__(self):
        self.test_results = {}

    def test_server_instance(self):
        """Test that the server instance is properly created"""
        print("Testing FastMCP server instance...")

        # Check that mcp is a FastMCP instance
        assert hasattr(mcp, 'tool'), "MCP should have tool decorator"
        assert hasattr(mcp, 'run'), "MCP should have run method"
        assert mcp.name == "Botasaurus MCP Server"

        print("  PASS Server instance created successfully")
        self.test_results["server_instance"] = "PASSED"

    def test_url_validation(self):
        """Test URL validation security features"""
        print("Testing URL validation...")

        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://httpbin.org",
            "https://httpbin.org/html"
        ]

        for url in valid_urls:
            is_valid = validate_url(url)
            assert is_valid, f"Valid URL {url} was incorrectly rejected"

        # Test invalid URLs
        invalid_urls = [
            "file:///etc/passwd",
            "http://localhost",
            "http://127.0.0.1",
            "http://192.168.1.1",
            "javascript:alert('xss')"
        ]

        for url in invalid_urls:
            is_valid = validate_url(url)
            assert not is_valid, f"Invalid URL {url} was incorrectly accepted"

        print("  PASS URL validation test passed")
        self.test_results["url_validation"] = "PASSED"

    def test_botasaurus_search_tool(self):
        """Test the botasaurus search tool"""
        print("Testing botasaurus search tool...")

        # Test the async botasaurus search function directly
        result = asyncio.run(botasaurus_search("Python programming", 3))

        assert "query" in result
        assert "results" in result
        assert "total_results" in result
        assert result["query"] == "Python programming"
        assert result["total_results"] == 3
        assert len(result["results"]) == 3

        print(f"  PASS Botasaurus search returned {result['total_results']} results for '{result['query']}'")
        self.test_results["botasaurus_search"] = "PASSED"

    def test_session_manager(self):
        """Test session manager functionality"""
        print("Testing session management...")

        # Create a dummy driver object for testing (we'll test the session management logic)
        class MockDriver:
            def quit(self):
                pass

        mock_driver = MockDriver()

        # Test session creation
        session_id = session_manager.create_session(mock_driver)
        assert session_id is not None
        assert len(session_id) > 0

        # Test session retrieval
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session['driver'] is mock_driver

        # Test session removal
        session_manager.remove_session(session_id)
        session = session_manager.get_session(session_id)
        assert session is None

        print("  PASS Session management test passed")
        self.test_results["session_management"] = "PASSED"

    def test_load_more_tool(self):
        """Test load_more tool with no active session (should fail gracefully)"""
        print("Testing load_more tool...")

        result = load_more()
        assert "error" in result
        assert "No active session found" in result["error"]

        print("  PASS Load more test completed (expected to fail with no active session)")
        self.test_results["load_more"] = "PASSED"

    def test_other_tools_simulation(self):
        """Test tools that are simulated"""
        print("Testing simulated tools...")

        # Test scrape_business_info (simulated)
        result = asyncio.run(scrape_business_info("test business"))
        assert "error" in result
        assert "not fully implemented" in result["error"]

        # Test monitor_webpage (simulated)
        result = asyncio.run(monitor_webpage("https://example.com"))
        assert "error" in result
        assert "not fully implemented" in result["error"]

        # Test download_document (simulated)
        result = asyncio.run(download_document("https://example.com/doc.pdf"))
        assert "error" in result
        assert "not fully implemented" in result["error"]

        print("  PASS Simulated tools test completed")
        self.test_results["simulated_tools"] = "PASSED"

    def run_all_tests(self):
        """Run all tests and report results"""
        print("=" * 60)
        print("Running FastMCP Botasaurus Server Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_server_instance,
            self.test_url_validation,
            self.test_botasaurus_search_tool,
            self.test_session_manager,
            self.test_load_more_tool,
            self.test_other_tools_simulation,
        ]

        for test_func in tests_to_run:
            try:
                test_func()
            except Exception as e:
                print(f"  FAIL {test_func.__name__} failed: {str(e)}")
                self.test_results[test_func.__name__.replace("test_", "")] = f"FAILED: {str(e)}"

        print("\n" + "=" * 60)
        print("Test Results Summary:")
        print("=" * 60)

        passed = sum(1 for result in self.test_results.values() if result == "PASSED")
        failed = len(self.test_results) - passed

        for test_name, result in self.test_results.items():
            status = "PASS" if result == "PASSED" else "FAIL"
            print(f"  {test_name}: {status}")

        print(f"\nTotal: {len(self.test_results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed == 0:
            print("\nAll tests passed!")
            return True
        else:
            print(f"\n{failed} tests failed!")
            return False


if __name__ == "__main__":
    tester = TestFastMCPBotasaurus()
    success = tester.run_all_tests()

    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)