import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.processing.website_checker import (
    classify_url_domain,
    check_url_with_httpx,
    verify_lead_website,
    STATUS_VALID_WEBSITE,
    STATUS_SOCIAL_ONLY,
    STATUS_DIRECTORY_ONLY,
    STATUS_NO_WEBSITE,
    STATUS_DOMAIN_ONLY,
    STATUS_BROKEN_WEBSITE,
    _country_google_code,
)
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestWebsiteChecker(unittest.TestCase):
    def test_classify_domain_type(self):
        self.assertEqual(classify_url_domain("https://www.facebook.com/mandapvadodara"), STATUS_SOCIAL_ONLY)
        self.assertEqual(classify_url_domain("https://instagram.com/barbequenation"), STATUS_SOCIAL_ONLY)
        self.assertEqual(classify_url_domain("https://www.justdial.com/Vadodara/Restaurants"), STATUS_DIRECTORY_ONLY)
        self.assertEqual(classify_url_domain("https://www.zomato.com/vadodara/mandap"), STATUS_DIRECTORY_ONLY)
        self.assertEqual(classify_url_domain("https://www.swiggy.com/restaurants/vadodara"), STATUS_DIRECTORY_ONLY)
        self.assertIsNone(classify_url_domain("https://www.mandaprestaurant.com"))

    def test_no_website(self):
        lead = Lead(name="Test Business", category="Cafe", city="Vadodara", source="test", website=None)
        status, verified_url, profile = verify_lead_website(lead)
        self.assertEqual(status, STATUS_NO_WEBSITE)
        self.assertIsNone(verified_url)

    def test_social_and_directory_classification(self):
        lead_social = Lead(name="My Restaurant", category="Food", city="Vadodara", source="test", website="https://facebook.com/myrestaurant")
        status, url, profile = verify_lead_website(lead_social)
        self.assertEqual(status, STATUS_SOCIAL_ONLY)

        lead_dir = Lead(name="My Restaurant", category="Food", city="Vadodara", source="test", website="https://justdial.com/Vadodara/MyRestaurant")
        status, url, profile = verify_lead_website(lead_dir)
        self.assertEqual(status, STATUS_DIRECTORY_ONLY)

    @patch("httpx.Client.get")
    def test_valid_website(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><head><title>Mandap Authentic Gujarati Restaurant Vadodara</title></head><body>Welcome to Mandap Restaurant</body></html>"
        mock_resp.url = "https://mandaprestaurant.com"
        mock_get.return_value = mock_resp

        status, profile = check_url_with_httpx("https://mandaprestaurant.com", "Mandap Restaurant")
        self.assertEqual(status, STATUS_VALID_WEBSITE)
        self.assertIn("seo_audit", profile)
        self.assertIn("seo_health_score", profile)

    def test_manchester_uses_uk_google_code(self):
        self.assertEqual(_country_google_code("Manchester"), "gb")

    def test_unknown_city_does_not_default_to_india(self):
        self.assertEqual(_country_google_code("Some Unknown City"), "")


if __name__ == "__main__":
    unittest.main()
