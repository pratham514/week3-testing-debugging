"""Short demonstration of the fixed cart (example from the report, Section 3.2).

Usage: python tools/demo_cart.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from cart import ShoppingCart

cart = ShoppingCart()
cart.add_item("Book", 50, 2)
cart.apply_coupon("save10")
print("Subtotal:", cart.subtotal())
print("Discount:", cart.discount())
print("Tax:     ", cart.tax())
print("Total:   ", cart.total())
print()
print(cart.receipt())
