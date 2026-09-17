import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.demo.url_generator import generate_lead_demo_urls, process_and_generate_demo_urls
from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database


class TestDemoSystem(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_url_generation(self):
        lead = Lead(
            name="Mandap Restaurant",
            category="Restaurant",
            city="Vadodara",
            source="test",
            id=101,
        )
        slug, demo_url, fallback_url = generate_lead_demo_urls(lead)
        self.assertIn("mandap-restaurant-vadodara", slug)
        self.assertIn("mandap-restaurant-vadodara", demo_url)


if __name__ == "__main__":
    unittest.main()
