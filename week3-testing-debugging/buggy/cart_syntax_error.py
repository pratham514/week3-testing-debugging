"""FIRST DRAFT of the shopping cart (contains a syntax error).

This file is kept only to document Bug B0 in the debugging report.
Running it fails immediately: python buggy/cart_syntax_error.py
"""


class ShoppingCart:
    def __init__(self, tax_rate=0.08, items={}):
        self.tax_rate = tax_rate
        self.items = items
        self.coupon = None

    def add_item(self, name, price, quantity=1)      # <-- B0: missing colon
        if price < 0:
            raise ValueError("price must be greater than 0")
        self.items[name] = [price, quantity]
