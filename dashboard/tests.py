import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def test_dashboard_page_renders(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/index.html")


class ReviewAPITests(TestCase):
    def setUp(self):
        self.url = reverse("dashboard:review-code")
        self.sample_review = {
            "summary": {
                "overview": "All good.",
                "highlights": ["Clean architecture"],
                "next_steps": ["Ship it"],
            },
            "critical": [],
            "best_practices": [],
            "performance": [],
            "strengths": ["Solid tests"],
        }

    @patch("dashboard.views.analyze_code")
    def test_review_success(self, analyze_code_mock):
        analyze_code_mock.return_value = self.sample_review

        response = self.client.post(
            self.url,
            data=json.dumps({"code": "print('ok')"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["overview"], "All good.")
        analyze_code_mock.assert_called_once()

    def test_invalid_json(self):
        response = self.client.post(self.url, data="not-json", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_empty_code(self):
        response = self.client.post(
            self.url, data=json.dumps({"code": "   "}), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

# Create your tests here.
