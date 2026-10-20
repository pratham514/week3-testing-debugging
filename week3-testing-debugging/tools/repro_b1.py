"""Reproduce bug B1: two separate carts should not share their items."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "buggy"))
from cart_buggy import ShoppingCart

first = ShoppingCart()
first.add_item("Pen", 2.5)
second = ShoppingCart()
print("Items in second (new) cart:", len(second), "(expected 0)")
