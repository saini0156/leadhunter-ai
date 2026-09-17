import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leadhunter.outreach.rate_limiter import RateLimiter
from leadhunter.outreach.email_sender import EmailSender, is_valid_email
from leadhunter.outreach.whatsapp_sender import WhatsAppSender
from leadhunter.db import Database
from leadhunter.models import Lead, LeadStatus


class TestOutreachExecution(unittest.TestCase):
    def setUp(self):
        self.db = Database(path=":memory:")

    def test_rate_limiter(self):
        limiter = RateLimiter(max_emails_per_hour=2, max_whatsapp_per_hour=3)
        self.assertTrue(limiter.can_send_email()[0])
        limiter.record_email()

    def test_email_validation(self):
        self.assertTrue(is_valid_email("owner@mandap.com"))
        self.assertFalse(is_valid_email(None))


if __name__ == "__main__":
    unittest.main()
