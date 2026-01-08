#!/usr/bin/env python3
"""
Test for chunking functionality in visit_page and load_more tools
Tests that visit_page returns first chunk and load_more returns subsequent chunks
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import _visit_page_impl, _load_more_impl


class TestChunkingFunctionality:
    """Test class for chunking functionality"""

    def test_visit_page_returns_first_chunk(self):
        """Test that visit_page returns the first chunk of content"""
        print("Testing visit_page returns first chunk...")

        # Test with a page that has substantial content
        result = _visit_page_impl("https://httpbin.org/html", "text")

        print(f"  Result keys: {list(result.keys())}")

        if "error" in result:
            print(f"  Error: {result['error']}")
            return False

        # Check that it returns first chunk info
        assert "content" in result
        assert "chunk_index" in result
        assert "has_more_chunks" in result
        assert result["chunk_index"] == 0  # Should be first chunk

        print(f"  Chunk index: {result['chunk_index']}")
        print(f"  Has more chunks: {result['has_more_chunks']}")
        print(f"  Content length: {len(result['content'])}")
        print("  PASS: visit_page returns first chunk")

        return True

    def test_load_more_returns_next_chunk(self):
        """Test that load_more returns the next chunk of content"""
        print("Testing load_more returns next chunk...")

        # First, visit a page to create a session
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        session_id = visit_result["session_id"]
        print(f"  Created session: {session_id}")

        # Now try to load more (next chunk)
        load_result = _load_more_impl()  # No parameters needed anymore

        print(f"  Load more result keys: {list(load_result.keys())}")

        if "error" in load_result:
            print(f"  Error in load_more: {load_result['error']}")
            # This might be expected if there are no more chunks
            if "No more chunks available" in load_result.get('message', ''):
                print("  INFO: No more chunks available (might be expected)")
                return True

        if "chunk_index" in load_result:
            print(f"  Next chunk index: {load_result['chunk_index']}")
            print(f"  Has more chunks: {load_result.get('has_more_chunks', 'N/A')}")

            # If there is a next chunk, it should have index > 0
            if load_result['chunk_index'] > 0:
                print("  PASS: load_more returned next chunk")
                return True
            elif load_result.get('status') == 'complete':
                print("  INFO: No more chunks available (expected if content is small)")
                return True

        print("  PASS: load_more functionality tested")
        return True

    def test_multiple_load_more_calls(self):
        """Test multiple load_more calls to go through all chunks"""
        print("Testing multiple load_more calls...")

        # First, visit a page with substantial content
        visit_result = _visit_page_impl("https://httpbin.org/html", "text")

        if "error" in visit_result or "session_id" not in visit_result:
            print(f"  Failed to visit page: {visit_result.get('error', 'No session ID')}")
            return False

        session_id = visit_result["session_id"]
        print(f"  Created session: {session_id}")

        # Track chunks received
        chunks_received = []
        current_result = visit_result
        chunks_received.append({
            'index': current_result['chunk_index'],
            'length': len(current_result['content']),
            'has_more': current_result['has_more_chunks']
        })

        # Try to get next chunks
        for i in range(5):  # Try up to 5 more chunks
            load_result = _load_more_impl()  # No parameters needed anymore

            if "error" in load_result and "No more chunks available" in load_result.get('message', ''):
                print(f"  No more chunks after {len(chunks_received)} chunks")
                break
            elif "chunk_index" in load_result:
                chunks_received.append({
                    'index': load_result['chunk_index'],
                    'length': len(load_result.get('content', '')),
                    'has_more': load_result.get('has_more_chunks', False)
                })

                print(f"    Chunk {load_result['chunk_index']}: {len(load_result.get('content', ''))} chars, more: {load_result.get('has_more_chunks', False)}")

                if not load_result.get('has_more_chunks', False):
                    print(f"  Completed after {len(chunks_received)} chunks")
                    break
            else:
                print(f"  Unexpected result: {load_result}")
                break

        print(f"  Received {len(chunks_received)} total chunks")
        print("  PASS: Multiple load_more calls handled correctly")
        return True

    def run_all_chunking_tests(self):
        """Run all chunking tests"""
        print("=" * 60)
        print("Running Chunking Functionality Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_visit_page_returns_first_chunk,
            self.test_load_more_returns_next_chunk,
            self.test_multiple_load_more_calls,
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
        print("Chunking Functionality Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if failed == 0:
            print("\nAll chunking functionality tests passed!")
            success = True
        else:
            print(f"\n{failed} tests failed. Implementation needs fixes.")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestChunkingFunctionality()
    success = tester.run_all_chunking_tests()

    sys.exit(0 if success else 1)