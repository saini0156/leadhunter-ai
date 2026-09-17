import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.approval.approval_queue import process_approval_queue
from leadhunter.approval.approval_viewer import ApprovalViewer
from leadhunter.outreach.email_sender import EmailSender
from leadhunter.outreach.whatsapp_sender import WhatsAppSender
from leadhunter.models import Lead, LeadStatus
from leadhunter.db import Database


class TestApprovalGate(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_enqueue_lead(self):
        lead = Lead(
            name="Mandap Restaurant",
            category="Restaurant",
            city="Vadodara",
            source="test",
            phone="+91 265 235 5555",
            email="contact@mandap.com",
            demo_url="http://localhost:8000/preview/mandap-restaurant-vadodara",
            status=LeadStatus.DEMO_READY,
        )
        lead_id, _ = self.db.insert_lead(lead)

        res = process_approval_queue(db=self.db, city="Vadodara", limit=10)
        self.assertIsNotNone(res)

        rows = self.db.conn.execute("SELECT * FROM approvals WHERE lead_id = ?", (lead_id,)).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["approval_status"], "PENDING_APPROVAL")


if __name__ == "__main__":
    unittest.main()
