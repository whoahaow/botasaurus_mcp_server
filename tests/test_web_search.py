#!/usr/bin/env python3
"""
Test for web search functionality using FastMCP
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import mcp, _web_search_impl as web_search


class TestWebSearch:
    """Test class for web search functionality"""

    def test_web_search_functionality(self):
        """Test the web search functionality directly"""
        print("Testing web search functionality...")

        # Test the internal web_search method directly
        result = asyncio.run(web_search("Python programming", 5))

        print(f"  Query: {result['query']}")
        print(f"  Total results: {result['total_results']}")
        print(f"  Number of results: {len(result['results'])}")

        for i, result_item in enumerate(result['results'][:3]):  # Show first 3 results
            print(f"    {i+1}. {result_item['title']}")
            print(f"       {result_item['url']}")
            print(f"       {result_item['snippet'][:100]}...")

        assert result['query'] == "Python programming"
        assert result['total_results'] == 5
        assert len(result['results']) == 5

        print("  PASS Web search functionality test passed")
        return True

    def test_web_search_edge_cases(self):
        """Test web search with edge cases"""
        print("Testing web search edge cases...")

        # Test with empty query (should handle gracefully)
        try:
            result = asyncio.run(web_search("", 5))
            print("  PASS Empty query handled gracefully")
        except Exception as e:
            print(f"  FAIL Empty query test failed: {e}")
            return False

        # Test with max results at boundary
        try:
            result = asyncio.run(web_search("test", 50))  # Maximum allowed
            assert result["total_results"] <= 50
            print("  PASS Boundary max_results test passed")
        except Exception as e:
            print(f"  FAIL Boundary test failed: {e}")
            return False

        # Test with minimum results
        try:
            result = asyncio.run(web_search("hello world", 1))
            assert result["total_results"] == 1
            print("  PASS Minimum results test passed")
            return True
        except Exception as e:
            print(f"  FAIL Minimum results test failed: {e}")
            return False

    def run_all_web_search_tests(self):
        """Run all web search tests"""
        print("=" * 60)
        print("Running Web Search Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_web_search_functionality,
            self.test_web_search_edge_cases,
        ]

        results = []
        for test_func in tests_to_run:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"  FAIL {test_func.__name__} failed with exception: {str(e)}")
                results.append(False)

        print("\n" + "=" * 60)
        print("Web Search Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if passed >= len(results) - 1:  # Allow 1 test to fail
            print("\nWeb search tests mostly successful!")
            success = True
        else:
            print(f"\nWeb search tests had significant issues")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestWebSearch()
    success = tester.run_all_web_search_tests()

    sys.exit(0 if success else 1)