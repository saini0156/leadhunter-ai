from leadhunter.models import Lead
from leadhunter.processing.lead_scorer import evaluate_lead

def test_seo_opportunity_scores_missing_website():
    lead = Lead(name="Test Plumbing", category="Plumber", city="Birmingham, United Kingdom",
                source="test", website_status="NO_WEBSITE", rating=4.5, reviews_count=10)
    score, tier, reasons, _ = evaluate_lead(lead, service="SEO")
    assert "SEO_OPPORTUNITY_WEAK_OR_MISSING_WEBSITE (+25)" in reasons
    assert score >= 25

def test_non_seo_keeps_legacy_behavior():
    lead = Lead(name="Test", category="plumber", city="Birmingham, United Kingdom",
                source="test", website_status="NO_WEBSITE")
    normal = evaluate_lead(lead, service="")
    seo = evaluate_lead(lead, service="SEO")
    assert seo[0] > normal[0]
