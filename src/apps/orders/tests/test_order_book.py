from django.test import SimpleTestCase

from apps.orders.exceptions import OrderError
from apps.orders.services import OrderBook


class OrderBookTests(SimpleTestCase):
    def setUp(self):
        self.book = OrderBook()

    def test_creates_and_lists_newest_first(self):
        first = self.book.create("Kigali Crafts", "A. Uwase", "local", "express", "1.5")
        second = self.book.create("Kigali Crafts", "B. Mugisha", "regional", "standard", 3)
        self.assertTrue(first.id.startswith("ONW-"))
        self.assertEqual(self.book.recent(), [second, first])

    def test_trims_names(self):
        order = self.book.create("  M  ", "  C  ", "local", "standard", 1)
        self.assertEqual((order.merchant, order.customer), ("M", "C"))

    def test_explains_missing_fields(self):
        cases = [
            (("", "C", "local", "standard", 1), "Enter the merchant name."),
            (("M", " ", "local", "standard", 1), "Enter the customer name."),
            (("M", "C", "local", "standard", "heavy"), "Enter the parcel weight"),
            (("M", "C", "local", "standard", None), "Enter the parcel weight"),
        ]
        for args, message in cases:
            with self.subTest(args=args), self.assertRaisesMessage(OrderError, message):
                self.book.create(*args)

    def test_keeps_a_bounded_history(self):
        for _ in range(205):
            self.book.create("M", "C", "local", "standard", 1)
        self.assertEqual(len(self.book.recent(1000)), 200)
