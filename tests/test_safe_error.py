"""
Tests for safe_user_message utility – security audit.
"""
import pytest
from utils.safe_error import safe_user_message


class TestSafeUserMessage:

    def test_known_timeout_error(self):
        msg = safe_user_message(TimeoutError("connection timed out"))
        assert "دیر شد" in msg
        assert "connection" not in msg   # raw message not leaked

    def test_known_value_error(self):
        msg = safe_user_message(ValueError("bad input"))
        assert "نامعتبر" in msg

    def test_generic_unknown_exception_no_traceback(self):
        class MyCustomError(Exception):
            pass

        msg = safe_user_message(MyCustomError("something weird happened"))
        # Should not expose Python traceback markers
        assert "Traceback" not in msg
        assert "File \"" not in msg

    def test_no_file_path_leakage(self):
        msg = safe_user_message(
            FileNotFoundError("/home/user/.secrets/token.txt not found")
        )
        # Path should be REDACTED or generic message returned
        assert "/home/user" not in msg

    def test_no_token_leakage(self):
        exc = Exception("API error: api_key=sk-abcdef1234567890")
        msg = safe_user_message(exc)
        assert "sk-abcdef" not in msg

    def test_no_ip_leakage(self):
        exc = ConnectionRefusedError("Cannot connect to 192.168.1.100:5432")
        msg = safe_user_message(exc)
        assert "192.168.1.100" not in msg

    def test_message_reasonable_length(self):
        long_exc = Exception("x" * 500)
        msg = safe_user_message(long_exc)
        # Hard cap is 80 chars for sanitised portion, message should be short
        assert len(msg) < 200

    def test_context_not_in_user_message(self):
        exc = Exception("db connection refused")
        msg = safe_user_message(exc, context="private_db_host=10.0.0.5")
        # Context is for logs only – should never appear in returned msg
        assert "10.0.0.5" not in msg
