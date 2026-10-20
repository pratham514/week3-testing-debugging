"""Reproduce bug B10: tax must be charged on the price AFTER the discount."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "buggy"))
from cart_buggy import ShoppingCart

cart = ShoppingCart(items={})
cart.add_item("Book", 50, 2)      # subtotal 100
cart.apply_coupon("SAVE10")       # discount 10
print("Tax:", cart.tax(), "(expected 7.2)")
print("Total:", cart.total(), "(expected 97.2)")
