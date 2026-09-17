import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.processing.lead_scorer import evaluate_lead, score_and_qualify_leads, TIER_HOT, TIER_WARM, TIER_LOW
from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database


class TestLeadScorer(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_hot_lead_broken_website(self):
        lead = Lead(
            name="Mandap Restaurant",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 265 235 5555",
            email="contact@mandaprestaurant.com",
            website_status="BROKEN_WEBSITE",
            rating=4.6,
            reviews_count=1250,
            tags={"instagram": "https://instagram.com/mandap"},
        )
        score, tier, reasons, qual_reason = evaluate_lead(lead, service="Digital Marketing")
        self.assertGreaterEqual(score, 70)
        self.assertEqual(tier, TIER_HOT)

    def test_hot_lead_no_website(self):
        lead = Lead(
            name="Shree Kathiyawadi Dhaba",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 98250 12345",
            website_status="NO_WEBSITE",
            rating=4.4,
            reviews_count=85,
        )
        score, tier, reasons, qual_reason = evaluate_lead(lead, service="Digital Marketing")
        self.assertGreaterEqual(score, 70)
        self.assertEqual(tier, TIER_HOT)

    def test_warm_lead_directory_only(self):
        lead = Lead(
            name="Saffron Dining",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 265 235 9999",
            website_status="DIRECTORY_ONLY",
            rating=3.8,
            reviews_count=12,
        )
        score, tier, reasons, qual_reason = evaluate_lead(lead, service="Digital Marketing")
        self.assertGreaterEqual(score, 45)

    def test_database_qualification_update(self):
        lead = Lead(
            name="Test Cafe",
            category="Cafe & Restaurant",
            city="Vadodara",
            source="test",
            phone="9876500000",
            website_status="NO_WEBSITE",
            status=LeadStatus.VERIFIED,
        )
        lead_id, _ = self.db.insert_lead(lead)

        scored_leads = score_and_qualify_leads(
            db=self.db,
            city="Vadodara",
            limit=10,
        )

        self.assertEqual(len(scored_leads), 1)
        self.assertIn(scored_leads[0]["lead_tier"], [TIER_HOT, TIER_WARM])
        self.assertEqual(scored_leads[0]["status"], LeadStatus.QUALIFIED.value)

        db_lead = self.db.get_lead(lead_id)
        self.assertEqual(db_lead.status, LeadStatus.QUALIFIED)
        self.assertIsNotNone(db_lead.score)
        self.assertIsNotNone(db_lead.lead_tier)


if __name__ == "__main__":
    unittest.main()
