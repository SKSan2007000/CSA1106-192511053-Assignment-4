
import unittest
from shopping_app import *

class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryOrderRepository()
        self.product = Product("P1","Pen",10.0,5)
        self.service = CheckoutService(self.repo, CardPayment())

    def test_successful_checkout_persists_order(self):
        order = self.service.checkout("O1", self.product, 2)
        self.assertEqual(order.status, "CONFIRMED")
        self.assertIs(self.repo.find("O1"), order)
        self.assertEqual(self.product.stock, 3)

    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.checkout("O2", self.product, 0)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.checkout("O3", self.product, -1)

    def test_insufficient_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.checkout("O4", self.product, 6)

    def test_upi_strategy(self):
        svc = CheckoutService(self.repo, UpiPayment())
        self.assertEqual(svc.checkout("O5", self.product, 1).status, "CONFIRMED")

    def test_missing_order_returns_none(self):
        self.assertIsNone(self.repo.find("missing"))

    def test_card_strategy_accepts_positive_amount(self):
        self.assertTrue(CardPayment().pay(10.0))

    def test_payment_strategy_rejects_zero_amount(self):
        self.assertFalse(UpiPayment().pay(0.0))

    def test_observers_receive_status_change(self):
        from io import StringIO
        from contextlib import redirect_stdout
        order = Order("O6", "P1", 1, 10.0)
        order.attach(EmailNotifier())
        order.attach(AdminNotifier())
        output = StringIO()
        with redirect_stdout(output):
            order.set_status("CONFIRMED")
        self.assertIn("EMAIL: order=O6", output.getvalue())
        self.assertIn("ADMIN: order=O6", output.getvalue())

if __name__ == "__main__":
    unittest.main()
