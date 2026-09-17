import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.ai.personalizer import generate_messages_for_lead, personalize_qualified_leads
from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database


class TestPersonalizer(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_broken_website_messaging(self):
        lead = Lead(
            name="Mandap Restaurant",
            city="Vadodara",
            category="Restaurant",
            source="test",
            website_status="BROKEN_WEBSITE",
            lead_tier="HOT",
        )
        res = generate_messages_for_lead(lead)
        self.assertIn("{{DEMO_URL}}", res["email_message"])
        self.assertIn("{{DEMO_URL}}", res["whatsapp_message"])
        self.assertLessEqual(len(res["email_subject"].split()), 8)

    def test_social_only_messaging(self):
        lead = Lead(
            name="Kathi Junction",
            city="Vadodara",
            category="Fast Food",
            source="test",
            website_status="SOCIAL_ONLY",
            lead_tier="HOT",
        )
        res = generate_messages_for_lead(lead)
        self.assertIn("{{DEMO_URL}}", res["email_message"])
        self.assertIn("{{DEMO_URL}}", res["whatsapp_message"])

    def test_no_website_opportunity_messaging(self):
        lead = Lead(
            name="Shree Kathiyawadi Dhaba",
            city="Vadodara",
            category="Dhaba",
            source="test",
            website_status="NO_WEBSITE",
            lead_tier="HOT",
        )
        res = generate_messages_for_lead(lead)
        self.assertIn("{{DEMO_URL}}", res["email_message"])
        self.assertIn("{{DEMO_URL}}", res["whatsapp_message"])

    def test_personalize_only_hot_and_warm(self):
        lead_hot = Lead(name="Hot Lead", city="Vadodara", category="Food", source="test", phone="9999900001", status=LeadStatus.QUALIFIED, lead_tier="HOT")
        self.db.insert_lead(lead_hot)

        results = personalize_qualified_leads(db=self.db, city="Vadodara", limit=10, delay_s=0.0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Hot Lead")
        self.assertEqual(results[0]["status"], LeadStatus.PERSONALIZED.value)


if __name__ == "__main__":
    unittest.main()
