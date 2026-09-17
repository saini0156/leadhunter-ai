import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.discovery.serpapi_search import search_serpapi_google_maps
from leadhunter.db import Database
from leadhunter.models import LeadStatus


class TestSerpAPIDiscovery(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    @patch("serpapi.Client.search")
    def test_successful_discovery(self, mock_search):
        mock_search.return_value = {
            "local_results": [
                {
                    "title": "Mandap Restaurant",
                    "type": "Gujarati Restaurant",
                    "phone": "+91 265 235 5555",
                    "address": "Alkapuri, Vadodara, Gujarat",
                    "website": "https://mandaprestaurant.com",
                    "rating": 4.6,
                    "reviews": 1250,
                    "place_id": "ChIJ_test1",
                    "link": "https://maps.google.com/?cid=12345"
                },
                {
                    "title": "Barbeque Nation",
                    "type": "Barbecue Restaurant",
                    "phone": "+91 265 618 8000",
                    "address": "Inorbit Mall, Gorwa Road, Vadodara",
                    "website": "https://barbequenation.com",
                    "rating": 4.4,
                    "reviews": 3400,
                    "place_id": "ChIJ_test2",
                    "link": "https://maps.google.com/?cid=67890"
                }
            ]
        }

        extracted, leads = search_serpapi_google_maps(
            city="Vadodara",
            business_type="restaurants",
            max_results=5,
            api_key="test_key",
            db=self.db
        )

        self.assertEqual(len(leads), 2)
        self.assertEqual(leads[0].name, "Mandap Restaurant")
        self.assertEqual(leads[0].city, "Vadodara")
        self.assertEqual(leads[0].status, LeadStatus.DISCOVERED)

        db_lead = self.db.get_lead(leads[0].id)
        self.assertIsNotNone(db_lead)
        self.assertEqual(db_lead.name, "Mandap Restaurant")


if __name__ == "__main__":
    unittest.main()
