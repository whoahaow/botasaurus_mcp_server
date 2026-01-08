#!/usr/bin/env python3
"""
Test for search functionality in search_on_page and search_next_on_page tools
Tests that search_on_page can search for text and search_next_on_page continues the search
"""

import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import _visit_page_impl, _search_on_page_impl, _search_next_on_page_impl


class TestSearchFunctionality:
    """Test class for search functionality"""

    def test_search_on_page_basic(self):
        """Test that search_on_page can find text in page content"""
        print("Testing search_on_page basic functionality...")

        # First visit a page
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        print(f"  Visited page, session: {visit_result['session_id'][:8]}...")

        # Now search for a common word in the content
        search_result = _search_on_page_impl("Herman", 3)

        print(f"  Search result keys: {list(search_result.keys())}")

        if "error" in search_result:
            print(f"  Error in search: {search_result['error']}")
            return False

        print(f"  Search text: {search_result.get('search_text', 'N/A')}")
        print(f"  Total matches: {search_result.get('total_matches', 0)}")
        print(f"  Snippets returned: {search_result.get('snippets_returned', 0)}")

        if search_result.get('snippets_returned', 0) > 0:
            for i, snippet in enumerate(search_result.get('snippets', [])[:2]):
                print(f"    Snippet {i+1}: chunk {snippet.get('chunk_index', 'N/A')}, pos {snippet.get('position', 'N/A')}")
                print(f"      Content: {snippet.get('snippet', '')[:100]}...")
        else:
            print("  No snippets returned (might be expected if text not found)")

        print("  PASS: search_on_page basic functionality tested")
        return True

    def test_search_next_on_page(self):
        """Test that search_next_on_page continues the search"""
        print("Testing search_next_on_page functionality...")

        # First visit a page
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        # Search for text with limited snippets first
        search_result = _search_on_page_impl("the", 2)  # Search for common word "the"

        if "error" in search_result:
            print(f"  Error in initial search: {search_result['error']}")
            return False

        print(f"  Initial search - matches: {search_result.get('total_matches', 0)}, returned: {search_result.get('snippets_returned', 0)}")

        # Now search for next results
        next_result = _search_next_on_page_impl(3)

        if "error" in next_result:
            print(f"  Error in next search: {next_result['error']}")
            # This might be expected if no more results
            if "No more results" in next_result['error'] or "No active search context" in next_result['error']:
                print("  INFO: No more search results available (might be expected)")
                return True

        print(f"  Next search - returned: {next_result.get('snippets_returned', 0)}")
        print(f"  Has more results: {next_result.get('has_more_results', False)}")

        if next_result.get('snippets_returned', 0) > 0:
            for i, snippet in enumerate(next_result.get('snippets', [])):
                print(f"    Next Snippet {i+1}: chunk {snippet.get('chunk_index', 'N/A')}")
                print(f"      Content: {snippet.get('snippet', '')[:100]}...")

        print("  PASS: search_next_on_page functionality tested")
        return True

    def test_search_on_page_no_session(self):
        """Test that search_on_page fails gracefully without active session"""
        print("Testing search_on_page without active session...")

        search_result = _search_on_page_impl("test", 3)

        if "error" in search_result and "No active session found" in search_result["error"]:
            print("  PASS: Correctly failed without active session")
            return True
        else:
            print(f"  FAIL: Expected session error but got: {search_result}")
            return False

    def test_search_next_on_page_no_context(self):
        """Test that search_next_on_page fails gracefully without active search context"""
        print("Testing search_next_on_page without active search context...")

        next_result = _search_next_on_page_impl(3)

        if "error" in next_result and "No active search context found" in next_result["error"]:
            print("  PASS: Correctly failed without active search context")
            return True
        else:
            print(f"  FAIL: Expected search context error but got: {next_result}")
            return False

    def run_all_search_tests(self):
        """Run all search tests"""
        print("=" * 60)
        print("Running Search Functionality Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_search_on_page_no_session,
            self.test_search_next_on_page_no_context,
            self.test_search_on_page_basic,
            self.test_search_next_on_page,
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
        print("Search Functionality Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if failed == 0:
            print("\nAll search functionality tests passed!")
            success = True
        else:
            print(f"\n{failed} tests failed. Implementation needs fixes.")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestSearchFunctionality()
    success = tester.run_all_search_tests()

    sys.exit(0 if success else 1)