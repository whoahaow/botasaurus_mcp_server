#!/usr/bin/env python3
"""
Test for read_chunk functionality
Tests that read_chunk can read specific chunk content
"""

import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import _visit_page_impl, _read_chunk_impl


class TestReadChunkFunctionality:
    """Test class for read_chunk functionality"""

    def test_read_chunk_basic(self):
        """Test that read_chunk can read content of a specific chunk"""
        print("Testing read_chunk basic functionality...")

        # First visit a page to create chunks
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        print(f"  Visited page, session: {visit_result['session_id'][:8]}...")

        # Try to read chunk 0
        read_result = _read_chunk_impl(0)

        print(f"  Read chunk result keys: {list(read_result.keys())}")

        if "error" in read_result:
            print(f"  Error in read_chunk: {read_result['error']}")
            return False

        print(f"  Chunk index: {read_result.get('chunk_index', 'N/A')}")
        print(f"  Total chunks: {read_result.get('total_chunks', 'N/A')}")
        print(f"  Chunk size: {read_result.get('chunk_size', 'N/A')}")

        content_preview = read_result.get('content', '')[:100]
        print(f"  Content preview: {content_preview}...")

        print("  PASS: read_chunk basic functionality tested")
        return True

    def test_read_chunk_out_of_range(self):
        """Test that read_chunk handles out of range chunk index"""
        print("Testing read_chunk with out of range index...")

        # First visit a page to create chunks
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        # Try to read a chunk that doesn't exist (assuming there are only 1-2 chunks)
        read_result = _read_chunk_impl(999)

        if "error" in read_result and "out of range" in read_result["error"]:
            print("  PASS: Correctly handled out of range chunk index")
            return True
        else:
            print(f"  FAIL: Expected out of range error but got: {read_result}")
            return False

    def test_read_chunk_negative_index(self):
        """Test that read_chunk handles negative chunk index"""
        print("Testing read_chunk with negative index...")

        # First visit a page to create chunks
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        # Try to read a chunk with negative index
        read_result = _read_chunk_impl(-1)

        if "error" in read_result and "out of range" in read_result["error"]:
            print("  PASS: Correctly handled negative chunk index")
            return True
        else:
            print(f"  FAIL: Expected out of range error but got: {read_result}")
            return False

    def test_read_chunk_no_session(self):
        """Test that read_chunk fails gracefully without active session"""
        print("Testing read_chunk without active session...")

        read_result = _read_chunk_impl(0)

        if "error" in read_result and "No active session found" in read_result["error"]:
            print("  PASS: Correctly failed without active session")
            return True
        else:
            print(f"  FAIL: Expected session error but got: {read_result}")
            return False

    def run_all_read_chunk_tests(self):
        """Run all read chunk tests"""
        print("=" * 60)
        print("Running Read Chunk Functionality Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_read_chunk_no_session,
            self.test_read_chunk_basic,
            self.test_read_chunk_out_of_range,
            self.test_read_chunk_negative_index,
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
        print("Read Chunk Functionality Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if failed == 0:
            print("\nAll read chunk functionality tests passed!")
            success = True
        else:
            print(f"\n{failed} tests failed. Implementation needs fixes.")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestReadChunkFunctionality()
    success = tester.run_all_read_chunk_tests()

    sys.exit(0 if success else 1)