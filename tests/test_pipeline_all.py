import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database


class TestCompletePipeline(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_pipeline_lead_lifecycle(self):
        lead = Lead(
            name="Mandap Restaurant",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 265 235 5555",
            status=LeadStatus.DISCOVERED,
        )
        lead_id, _ = self.db.insert_lead(lead)
        self.db.update_lead(lead_id, {"status": LeadStatus.VERIFIED.value})
        db_lead = self.db.get_lead(lead_id)
        self.assertEqual(db_lead.status, LeadStatus.VERIFIED)


if __name__ == "__main__":
    unittest.main()
