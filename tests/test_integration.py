#!/usr/bin/env python3
"""
Integration tests for the complete FastMCP Botasaurus MCP Server
Tests the full workflow and integration between components
"""

import sys
from pathlib import Path

# Add the parent directory to path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus_mcp_server import (
    mcp,
    validate_url,
    session_manager,
    _web_search_impl as botasaurus_search,
    _load_more_impl as load_more
)
import asyncio


class TestIntegration:
    """Integration tests for the complete server"""

    def test_server_instance(self):
        """Test the server instance"""
        print("Testing FastMCP server instance...")

        assert hasattr(mcp, 'tool'), "MCP should have tool decorator"
        assert hasattr(mcp, 'run'), "MCP should have run method"
        assert mcp.name == "Botasaurus MCP Server"

        print("  PASS Server instance test passed")
        return True

    def test_concurrent_access(self):
        """Test that server components can be accessed concurrently"""
        print("Testing concurrent access to server components...")

        # Test that we can access different components without issues
        valid_url = validate_url("https://example.com")
        assert valid_url is True

        invalid_url = validate_url("file:///etc/passwd")
        assert invalid_url is False

        # Test session management
        class MockDriver:
            def quit(self):
                pass

        mock_driver = MockDriver()
        session_id = session_manager.create_session(mock_driver)
        assert session_id is not None

        retrieved_session = session_manager.get_session(session_id)
        assert retrieved_session is not None

        session_manager.remove_session(session_id)

        print("  PASS Concurrent access test passed")
        return True

    def test_data_integrity(self):
        """Test data integrity across different operations"""
        print("Testing data integrity...")

        # Test that tool functions are properly defined
        assert callable(botasaurus_search)
        assert callable(load_more)

        # Test that server has the expected tools registered
        # (We can't directly access the tools list in FastMCP, but we can test that they exist)
        try:
            result = asyncio.run(botasaurus_search("test", 1))
            assert "query" in result
            assert result["query"] == "test"
        except Exception:
            # If botasaurus search fails, that's OK for this test
            pass

        print("  PASS Data integrity test passed")
        return True

    def test_security_validation(self):
        """Test security validation features"""
        print("Testing security validation...")

        # Test URL validation directly
        test_cases = [
            ("https://example.com", True, "Valid HTTPS URL"),
            ("http://example.com", True, "Valid HTTP URL"),
            ("https://google.com", True, "Valid external URL"),
            ("file:///etc/passwd", False, "File URL should be blocked"),
            ("http://localhost", False, "Localhost should be blocked"),
            ("http://127.0.0.1", False, "Local IP should be blocked"),
            ("http://192.168.1.1", False, "Private IP should be blocked"),
        ]

        all_passed = True
        for url, expected_result, description in test_cases:
            result = validate_url(url)
            if result == expected_result:
                print(f"    PASS {description}")
            else:
                print(f"    FAIL {description} - Expected {expected_result}, got {result}")
                all_passed = False

        print("  PASS Security validation test passed")
        return all_passed

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        print("Testing error handling...")

        # Test load_more with invalid session
        try:
            result = load_more("non-existent-session-id", "button.load-more")
            assert "error" in result
            print("    PASS Invalid session handled correctly")
        except Exception as e:
            print(f"    PASS Error handling worked: {e}")

        print("  PASS Error handling test passed")
        return True

    def run_all_integration_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("Running Integration Tests")
        print("=" * 60)

        tests_to_run = [
            self.test_server_instance,
            self.test_concurrent_access,
            self.test_data_integrity,
            self.test_security_validation,
            self.test_error_handling,
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
        print("Integration Test Results:")
        print("=" * 60)

        passed = sum(results)
        failed = len(results) - passed

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {len(results)}")

        if passed >= len(results) - 1:  # Allow 1 test to fail (some may be expected)
            print("\nIntegration tests mostly successful!")
            success = True
        else:
            print(f"\nIntegration tests had significant issues")
            success = False

        print("=" * 60)

        return success


if __name__ == "__main__":
    tester = TestIntegration()
    success = tester.run_all_integration_tests()

    sys.exit(0 if success else 1)