import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib
from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database

app_module = importlib.import_module("leadhunter.web.app")


class TestExportCSV(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")
        self.client = TestClient(app_module.app)
        self.orig_get_db = app_module.get_db
        app_module.get_db = lambda: self.db

        lead = Lead(
            name="Test SEO Client",
            category="Dentist",
            city="Toronto, Canada",
            source="test",
            phone="+14165550199",
            email="info@testclient.com",
            website="http://testclient.com",
            website_status="VALID_WEBSITE",
            lead_tier="HOT",
            score=85.0,
            status=LeadStatus.QUALIFIED,
        )
        self.db.insert_lead(lead)

    def tearDown(self):
        app_module.get_db = self.orig_get_db

    def test_export_csv_endpoint(self):
        response = self.client.get("/api/export/csv?city=Toronto%2C+Canada")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn("attachment; filename=", response.headers["content-disposition"])
        # Ensure no commas in content-disposition header to prevent ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_DISPOSITION
        self.assertNotIn(",", response.headers["content-disposition"])
        content = response.content.decode("utf-8")
        self.assertTrue(content.startswith("\ufeff"))
        self.assertIn("Test SEO Client", content)
        self.assertIn("Toronto", content)
        self.assertIn("Dentist", content)


if __name__ == "__main__":
    unittest.main()
