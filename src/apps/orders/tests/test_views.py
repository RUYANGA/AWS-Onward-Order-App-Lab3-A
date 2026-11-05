from django.test import Client, SimpleTestCase

from apps.orders.services import book

VALID_FORM = {
    "merchant": "Kigali Crafts",
    "customer": "A. Uwase",
    "zone": "local",
    "service": "standard",
    "weight_kg": "2",
}


class OrderPageTests(SimpleTestCase):
    def test_home_shows_name_lab_release_and_env(self):
        body = self.client.get("/").content.decode()
        self.assertIn("Onward Logistics", body)
        self.assertIn("Test Student", body)
        self.assertIn("Delivering Order System Updates Safely for Onward Logistics", body)
        self.assertIn('class="release">test<', body)

    def test_place_order_via_form(self):
        response = self.client.post("/orders", VALID_FORM)
        self.assertEqual(response.status_code, 302)
        order_id = book.recent(1)[0].id
        self.assertEqual(response["Location"], f"/?placed={order_id}")
        page = self.client.get(response["Location"]).content.decode()
        self.assertIn(f"Order {order_id} booked.", page)
        self.assertIn("Kigali Crafts", page)

    def test_form_error_is_explained_and_values_kept(self):
        response = self.client.post("/orders", {**VALID_FORM, "merchant": ""})
        self.assertEqual(response.status_code, 400)
        body = response.content.decode()
        self.assertIn("Enter the merchant name.", body)
        self.assertIn('value="A. Uwase"', body)

    def test_form_requires_csrf_token(self):
        strict = Client(enforce_csrf_checks=True)
        self.assertEqual(strict.post("/orders", VALID_FORM).status_code, 403)

    def test_form_only_accepts_post(self):
        self.assertEqual(self.client.get("/orders").status_code, 405)
