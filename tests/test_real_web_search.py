#!/usr/bin/env python3
"""
Real tests for web search functionality using FastMCP
Tests actual web search functionality instead of mock results
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import mcp, _web_search_impl as botasaurus_search


class TestRealBotasaurusSearch:
    """Test class for real botasaurus search functionality"""

    def test_real_botasaurus_search_functionality(self):
        """Test the botasaurus search functionality with real search"""
        print("Testing real botasaurus search functionality...")

        # Test with a real search query
        result = asyncio.run(botasaurus_search("Python programming", 3))

        print(f"  Query: {result['query']}")
        print(f"  Total results: {result['total_results']}")
        print(f"  Number of results: {len(result['results'])}")

        if result['total_results'] > 0:
            for i, result_item in enumerate(result['results'][:3]):  # Show first 3 results
                print(f"    {i+1}. {result_item['title']}")
                print(f"       {result_item['url']}")
                print(f"       {result_item['snippet'][:100]}...")

        # Basic assertions - these will fail if the implementation is still mock
        assert result['query'] == "Python programming"
        assert result['total_results'] <= 3  # Should be at most 3 results
        assert len(result['results']) <= 3

        # If results are mock (example.com), this test should fail
        mock_results = all("example.com" in item['url'] for item in result['results'])
        if mock_results:
            print("  FAIL: Search returned mock results (example.com URLs)")
            return False

        print("  PASS: Botasaurus search returned real results")
        return True

    def test_real_botasaurus_search_diverse_queries(self):
        """Test botasaurus search with diverse queries to ensure real functionality"""
        print("Testing real botasaurus search with diverse queries...")

        test_queries = [
            ("openai", 2),
            ("wikipedia", 2),
            ("python.org", 1)
        ]

        all_passed = True
        for query, max_results in test_queries:
            print(f"    Testing query: '{query}'")
            result = asyncio.run(botasaurus_search(query, max_results))

            if result['query'] == query:
                print(f"      Returned {result['total_results']} results")

                # Check if results are from mock implementation
                if result['total_results'] > 0:
                    mock_results = all("example.com" in item['url'] for item in result['results'])
                    if mock_results:
                        print(f"      FAIL: Query '{query}' returned mock results")
                        all_passed = False
                    else:
                        print(f"      PASS: Query '{query}' returned real results")
                else:
                    print(f"      INFO: Query '{query}' returned no results (might be valid)")
            else:
                print(f"      FAIL: Query '{query}' failed")
                all_passed = False

        if all_passed:
            print("  PASS: All diverse queries returned real results")
        else:
            print("  FAIL: Some queries returned mock results")

        return all_passed

    def test_real_botasaurus_search_edge_cases(self):
        """Test botasaurus search with edge cases"""
        print("Testing real botasaurus search edge cases...")

        # Test with empty query (should handle gracefully)
        try:
            result = asyncio.run(botasaurus_search("", 1))
            print("  PASS: Empty query handled gracefully")
        except Exception as e:
            print(f"  INFO: Empty query test failed as expected: {e}")

        # Test with unusual characters
        try:
            result = asyncio.run(botasaurus_search("test & symbol @#$", 1))
            mock_results = all("example.com" in item['url'] for item in result['results'])
            if mock_results:
                print("  FAIL: Special characters query returned mock results")
                return False
            else:
                print("  PASS: Special characters query handled properly")
        except Exception as e:
            print(f"  INFO: Special characters query failed as expected: {e}")

        return True

    def run_all_real_botasaurus_search_tests(self):
        """Run all real botasaurus search tests"""
        print("=" * 60)
        print("Running Real Botasaurus Search Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_real_botasaurus_search_functionality,
            self.test_real_botasaurus_search_diverse_queries,
            self.test_real_botasaurus_search_edge_cases,
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
        print("Real Web Search Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if failed == 0:
            print("\nAll real web search tests passed! Implementation is working correctly.")
            success = True
        elif passed > 0:
            print(f"\nSome tests passed ({passed}), but {failed} failed. Implementation needs fixes.")
            success = False
        else:
            print(f"\nAll tests failed ({failed}). Implementation needs complete fix.")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestRealBotasaurusSearch()
    success = tester.run_all_real_botasaurus_search_tests()

    sys.exit(0 if success else 1)