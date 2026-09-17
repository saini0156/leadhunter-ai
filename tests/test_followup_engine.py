import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.followup.followup_engine import FollowupEngine
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestFollowupEngine(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_followup_engine_check(self):
        engine = FollowupEngine(db=self.db)
        results = engine.check_and_stage_followups(city="Vadodara", limit=10)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
