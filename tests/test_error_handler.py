import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.utils.error_handler import classify_error, retry_with_backoff
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestErrorHandlerAndResume(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_classify_error_types(self):
        self.assertEqual(classify_error(Exception("HTTP 429: Too Many Requests")), "RATE_LIMIT")
        self.assertEqual(classify_error(Exception("HTTP 401 Unauthorized: Invalid API key")), "AUTH_ERROR")

    def test_retry_with_backoff_transient(self):
        call_count = 0
        def flappy_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Connection reset by peer (502)")
            return "SUCCESS"

        result = retry_with_backoff(flappy_function, max_retries=2, base_delay=0.01)
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(call_count, 2)


if __name__ == "__main__":
    unittest.main()
