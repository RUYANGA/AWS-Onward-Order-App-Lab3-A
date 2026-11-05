from django.test import Client, SimpleTestCase

ORDER = {
    "merchant": "Load Test",
    "customer": "Bot",
    "zone": "national",
    "service": "express",
    "weight_kg": 4,
}


class QuoteApiTests(SimpleTestCase):
    def test_returns_price_and_days(self):
        response = self.client.get(
            "/api/quote", {"zone": "local", "service": "standard", "weight_kg": "2"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"price": 6.4, "delivery_days": 1})

    def test_bad_input_is_400(self):
        for params in (
            {"zone": "moon"},
            {"zone": "local", "service": "standard", "weight_kg": "x"},
        ):
            with self.subTest(params=params):
                response = self.client.get("/api/quote", params)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())


class OrdersApiTests(SimpleTestCase):
    def post(self, data, client=None):
        return (client or self.client).post("/api/orders", data, content_type="application/json")

    def test_round_trip(self):
        created = self.post(ORDER)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["price"], 26.88)
        self.assertEqual(self.client.get("/api/orders").json()[0]["id"], created.json()["id"])

    def test_invalid_order_is_400(self):
        response = self.post({**ORDER, "zone": "moon"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_malformed_body_is_400(self):
        for body in ("not json", "[1, 2]"):
            with self.subTest(body=body):
                response = self.post(body)
                self.assertEqual(response.status_code, 400)

    def test_needs_no_csrf_token(self):
        self.assertEqual(self.post(ORDER, Client(enforce_csrf_checks=True)).status_code, 201)
