import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.sheets_logger import SheetsLogger
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestSheetsLogger(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")
        self.logger = SheetsLogger(db=self.db)

    def test_sheets_logger_init(self):
        self.assertIsNotNone(self.logger)


if __name__ == "__main__":
    unittest.main()
