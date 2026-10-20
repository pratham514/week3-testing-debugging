"""Unit tests for the shopping cart.

By default the tests run against the FIXED module (src/cart.py).
To run the same tests against the ORIGINAL buggy module, set the
environment variable CART_MODULE=cart_buggy (or use tools/run_against_buggy.py).
"""
import importlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "buggy"))

ShoppingCart = importlib.import_module(os.environ.get("CART_MODULE", "cart")).ShoppingCart


class AddItemTests(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()

    def test_add_single_item(self):
        self.cart.add_item("Pen", 2.5)
        self.assertEqual(self.cart.quantity_of("Pen"), 1)
        self.assertEqual(len(self.cart), 1)

    def test_add_with_quantity(self):
        self.cart.add_item("Pen", 2.5, 4)
        self.assertEqual(self.cart.quantity_of("Pen"), 4)

    def test_adding_existing_item_increases_quantity(self):          # B2
        self.cart.add_item("Pen", 2.5, 2)
        self.cart.add_item("Pen", 2.5, 3)
        self.assertEqual(self.cart.quantity_of("Pen"), 5)
        self.assertEqual(len(self.cart), 1)

    def test_price_zero_rejected(self):                              # B3
        with self.assertRaises(ValueError):
            self.cart.add_item("Free", 0)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            self.cart.add_item("Bad", -5)

    def test_zero_quantity_rejected(self):                           # B4
        with self.assertRaises(ValueError):
            self.cart.add_item("Pen", 2.5, 0)

    def test_negative_quantity_rejected(self):                       # B4
        with self.assertRaises(ValueError):
            self.cart.add_item("Pen", 2.5, -3)

    def test_non_integer_quantity_rejected(self):                    # B4
        with self.assertRaises(ValueError):
            self.cart.add_item("Pen", 2.5, 1.5)


class RemoveItemTests(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()
        self.cart.add_item("Pen", 2.5, 5)

    def test_remove_whole_item(self):
        self.cart.remove_item("Pen")
        self.assertEqual(len(self.cart), 0)
        self.assertEqual(self.cart.quantity_of("Pen"), 0)

    def test_remove_part_of_quantity(self):
        self.cart.remove_item("Pen", 2)
        self.assertEqual(self.cart.quantity_of("Pen"), 3)

    def test_removing_exact_quantity_deletes_item(self):             # B5
        self.cart.remove_item("Pen", 5)
        self.assertEqual(len(self.cart), 0)
        self.assertEqual(self.cart.total_quantity(), 0)

    def test_removing_too_many_raises(self):                         # B5
        with self.assertRaises(ValueError):
            self.cart.remove_item("Pen", 9)
        self.assertEqual(self.cart.quantity_of("Pen"), 5)

    def test_remove_missing_item_raises(self):
        with self.assertRaises(KeyError):
            self.cart.remove_item("Nope")

    def test_remove_zero_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.cart.remove_item("Pen", 0)


class MoneyTests(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()

    def test_empty_cart_totals_are_zero(self):
        self.assertEqual(self.cart.subtotal(), 0)
        self.assertEqual(self.cart.total(), 0)

    def test_subtotal_uses_quantity(self):
        self.cart.add_item("Pen", 2.5, 4)
        self.cart.add_item("Book", 10, 1)
        self.assertEqual(self.cart.subtotal(), 20.0)

    def test_subtotal_is_rounded(self):                              # B6
        self.cart.add_item("A", 0.1)
        self.cart.add_item("B", 0.2)
        self.assertEqual(self.cart.subtotal(), 0.3)

    def test_tax_without_coupon(self):
        self.cart.add_item("Book", 50, 2)
        self.assertEqual(self.cart.tax(), 8.0)
        self.assertEqual(self.cart.total(), 108.0)

    def test_tax_is_charged_after_discount(self):                    # B10
        self.cart.add_item("Book", 50, 2)
        self.cart.apply_coupon("SAVE10")
        self.assertEqual(self.cart.discount(), 10.0)
        self.assertEqual(self.cart.tax(), 7.2)
        self.assertEqual(self.cart.total(), 97.2)

    def test_custom_tax_rate(self):
        cart = ShoppingCart(tax_rate=0.5)
        cart.add_item("Book", 10)
        self.assertEqual(cart.total(), 15.0)

    def test_total_is_rounded_to_two_decimals(self):                 # B6
        self.cart.add_item("Thing", 3.33, 3)
        self.assertEqual(self.cart.total(), round(self.cart.total(), 2))
        self.assertEqual(self.cart.total(), 10.79)


class CouponTests(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()
        self.cart.add_item("Chair", 60, 2)       # subtotal 120

    def test_save10_gives_ten_percent(self):
        self.cart.apply_coupon("SAVE10")
        self.assertEqual(self.cart.discount(), 12.0)

    def test_save20_gives_twenty_percent(self):
        self.cart.apply_coupon("SAVE20")
        self.assertEqual(self.cart.discount(), 24.0)

    def test_save20_accepted_at_exactly_100(self):                   # B7
        cart = ShoppingCart()
        cart.add_item("Desk", 100)
        cart.apply_coupon("SAVE20")
        self.assertEqual(cart.discount(), 20.0)

    def test_save20_rejected_below_100(self):
        cart = ShoppingCart()
        cart.add_item("Desk", 99.99)
        with self.assertRaises(ValueError):
            cart.apply_coupon("SAVE20")

    def test_unknown_coupon_raises(self):                            # B8
        with self.assertRaises(ValueError):
            self.cart.apply_coupon("BOGUS")

    def test_coupon_code_is_case_insensitive(self):                  # B9
        self.cart.apply_coupon("save10")
        self.assertEqual(self.cart.discount(), 12.0)

    def test_coupon_code_ignores_surrounding_spaces(self):           # B9
        self.cart.apply_coupon("  SAVE10 ")
        self.assertEqual(self.cart.discount(), 12.0)

    def test_new_coupon_replaces_old_one(self):
        self.cart.apply_coupon("SAVE10")
        self.cart.apply_coupon("SAVE20")
        self.assertEqual(self.cart.discount(), 24.0)

    def test_no_coupon_means_no_discount(self):
        self.assertEqual(self.cart.discount(), 0)

    def test_save20_stops_applying_if_subtotal_drops_below_100(self):  # B14
        self.cart.apply_coupon("SAVE20")
        self.cart.remove_item("Chair", 1)        # subtotal now 60
        self.assertEqual(self.cart.discount(), 0)
        self.assertEqual(self.cart.total(), 64.8)


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()

    def test_average_price_is_per_unit(self):                        # B11
        self.cart.add_item("Pen", 2, 3)          # 6.00
        self.cart.add_item("Book", 14, 1)        # 14.00 -> 20 / 4 units
        self.assertEqual(self.cart.average_item_price(), 5.0)

    def test_average_price_of_empty_cart_is_zero(self):              # B12
        self.assertEqual(self.cart.average_item_price(), 0.0)

    def test_most_expensive_item_uses_price(self):                   # B13
        self.cart.add_item("Pen", 2, 10)
        self.cart.add_item("Laptop", 900, 1)
        self.assertEqual(self.cart.most_expensive_item(), "Laptop")

    def test_most_expensive_item_of_empty_cart_is_none(self):
        self.assertIsNone(self.cart.most_expensive_item())

    def test_total_quantity(self):
        self.cart.add_item("Pen", 2, 3)
        self.cart.add_item("Book", 14, 2)
        self.assertEqual(self.cart.total_quantity(), 5)


class ReceiptTests(unittest.TestCase):
    def test_receipt_contains_lines_and_totals(self):
        cart = ShoppingCart()
        cart.add_item("Pen", 2.5, 4)
        cart.add_item("Book", 10, 1)
        cart.apply_coupon("SAVE10")
        text = cart.receipt()
        self.assertIn("Pen", text)
        self.assertIn("Book", text)
        self.assertIn("Subtotal:", text)
        self.assertTrue(text.splitlines()[-1].endswith("19.44"))   # (20-2)*1.08
        self.assertIn("-2.00", text)


class IsolationTests(unittest.TestCase):
    def test_carts_do_not_share_items(self):                         # B1
        first = ShoppingCart()
        first.add_item("Pen", 2.5)
        second = ShoppingCart()
        self.assertEqual(len(second), 0)

    def test_carts_do_not_share_coupons(self):
        first = ShoppingCart()
        first.add_item("Desk", 200)
        first.apply_coupon("SAVE10")
        second = ShoppingCart()
        second.add_item("Desk", 200)
        self.assertEqual(second.discount(), 0)


if __name__ == "__main__":
    unittest.main()
