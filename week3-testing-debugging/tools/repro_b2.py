"""Reproduce bug B2: adding an existing item should add to its quantity."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "buggy"))
from cart_buggy import ShoppingCart

cart = ShoppingCart(items={})   # fresh dict, to keep bug B1 out of the way
cart.add_item("Pen", 2.5, 2)
cart.add_item("Pen", 2.5, 3)
print("Pen quantity:", cart.quantity_of("Pen"), "(expected 5)")
