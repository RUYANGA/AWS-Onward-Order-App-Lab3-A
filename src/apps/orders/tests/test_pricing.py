from django.test import SimpleTestCase

from apps.orders.exceptions import OrderError
from apps.orders.services import quote


class QuoteTests(SimpleTestCase):
    def test_express_is_faster_and_dearer(self):
        std_price, std_days = quote("national", "standard", 2)
        exp_price, exp_days = quote("national", "express", 2)
        self.assertGreater(exp_price, std_price)
        self.assertLess(exp_days, std_days)

    def test_local_standard_price(self):
        self.assertEqual(quote("local", "standard", 2), (6.4, 1))

    def test_delivery_takes_at_least_one_day(self):
        _, days = quote("local", "express", 1)
        self.assertEqual(days, 1)

    def test_rejects_bad_input(self):
        cases = [
            ("moon", "standard", 1),
            ("local", "drone", 1),
            ("local", "standard", 0),
            ("local", "standard", 51),
            ("local", "standard", float("nan")),
        ]
        for zone, service, weight in cases:
            with self.subTest(zone=zone, weight=weight), self.assertRaises(OrderError):
                quote(zone, service, weight)
