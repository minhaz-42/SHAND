from django.test import TestCase, Client
from .assumption_detector import detect_assumptions
from .assumption_classifier import classify_assumption
from .risk_engine import assess_risk


class EngineUnitTests(TestCase):
    def test_detector_finds_assumption(self):
        text = "We will launch the product next quarter. We assume customers will adopt it."
        cands = detect_assumptions(text)
        texts = [c['assumption_text'].lower() for c in cands]
        self.assertTrue(any('launch the product next quarter' in t or 'launch the product' in t for t in texts))
        self.assertTrue(any('customers will adopt it' in t or 'customers will adopt' in t for t in texts))

    def test_classifier_basic(self):
        out = classify_assumption('users will prefer the new UI')
        self.assertEqual(out['type'], 'Behavioral')
        self.assertGreaterEqual(out['confidence'], 0.6)

    def test_risk_engine_scope(self):
        r = assess_risk('All users will switch to the new platform')
        self.assertEqual(r['level'], 'HIGH')

    def test_api_endpoint(self):
        client = Client()
        resp = client.post('/analyze/', {'text': 'We assume this will work.'}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('assumptions', data)
        self.assertIn('graph', data)
