import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.processing.normalize import (
    normalize_name,
    normalize_phone,
    normalize_website,
    extract_domain,
    normalize_address,
    compute_quality_score,
)
from leadhunter.processing.deduplicate import process_leads
from leadhunter.dedup import primary_fingerprint
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestNormalizeAndDeduplicate(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_normalize_business_name(self):
        self.assertEqual(normalize_name("Barbeque Nation Pvt. Ltd."), "barbeque nation")
        self.assertEqual(normalize_name("The Grand Thakar & Caterers Private Limited"), "the grand thakar caterers")

    def test_normalize_phone(self):
        self.assertEqual(normalize_phone("+91 265 235 5555"), "2652355555")

    def test_normalize_website(self):
        self.assertEqual(normalize_website("https://www.mandaprestaurant.com/"), "mandaprestaurant.com")
        self.assertEqual(extract_domain("https://www.barbequenation.com/outlets/vadodara"), "barbequenation.com")

    def test_quality_score_calculation(self):
        full_lead = Lead(
            name="Full Restaurant",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 9876543210",
            website="https://fullrest.com",
            address="Alkapuri, Vadodara",
            email="contact@fullrest.com",
            rating=4.5,
            reviews_count=120,
        )
        score, reasons = compute_quality_score(full_lead)
        self.assertEqual(score, 100)

    def test_primary_fingerprint(self):
        fp1 = primary_fingerprint("Mandap Restaurant", "Vadodara", "Food", "9876543210")
        fp2 = primary_fingerprint("Mandap Restaurant", "Vadodara", "Food", "+91 9876543210")
        self.assertEqual(fp1, fp2)


if __name__ == "__main__":
    unittest.main()
