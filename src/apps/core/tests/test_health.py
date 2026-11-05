from django.test import SimpleTestCase, override_settings

from apps.core.health import HEALTH_PATH

# Mimic a tightened production: a real domain in ALLOWED_HOSTS and HTTPS enforced.
PRODUCTION_LIKE = {"ALLOWED_HOSTS": ["orders.example.com"], "SECURE_SSL_REDIRECT": True}
ALB_PRIVATE_IP = "10.20.10.5"


class HealthCheckTests(SimpleTestCase):
    def test_reports_ok_with_release_and_task(self):
        response = self.client.get(HEALTH_PATH)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["version"], "test")
        self.assertIn("task", body)
        self.assertIn("zone", body)

    def test_head_request_is_supported(self):
        self.assertEqual(self.client.head(HEALTH_PATH).status_code, 200)


@override_settings(**PRODUCTION_LIKE)
class HealthCheckBehindLoadBalancerTests(SimpleTestCase):
    def test_load_balancer_check_on_private_ip_over_http(self):
        response = self.client.get(HEALTH_PATH, headers={"host": ALB_PRIVATE_IP})
        self.assertEqual(response.status_code, 200)

    def test_other_paths_still_reject_unknown_hosts(self):
        response = self.client.get("/", headers={"host": ALB_PRIVATE_IP})
        self.assertEqual(response.status_code, 400)

    def test_other_paths_still_redirect_to_https(self):
        response = self.client.get("/", headers={"host": "orders.example.com"})
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response["Location"].startswith("https://"))
