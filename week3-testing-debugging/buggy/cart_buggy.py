# cart_buggy.py - ORIGINAL version of the shopping cart (deliberately flawed).
# Syntax error B0 has been fixed here; the logic bugs B1-B14 are still present.
# Do not use this file in real code. It exists to be tested and debugged.


class ShoppingCart:
    def __init__(self, tax_rate=0.08, items={}):          # B1: mutable default argument
        self.tax_rate = tax_rate
        self.items = items
        self.coupon = None

    def add_item(self, name, price, quantity=1):
        if price < 0:                                      # B3: price 0 is accepted
            raise ValueError("price must be greater than 0")
        # B4: quantity is never validated (0 and negatives accepted)
        if name in self.items:
            self.items[name] = [price, quantity]           # B2: overwrites instead of adding
        else:
            self.items[name] = [price, quantity]

    def remove_item(self, name, quantity=None):
        if name not in self.items:
            raise KeyError(name)
        if quantity is None:
            del self.items[name]
        else:
            self.items[name][1] = self.items[name][1] - quantity
            if self.items[name][1] < 0:                    # B5: leaves quantity 0, allows over-removal
                del self.items[name]

    def quantity_of(self, name):
        if name in self.items:
            return self.items[name][1]
        return 0

    def total_quantity(self):
        total = 0
        for name in self.items:
            total = total + self.items[name][1]
        return total

    def __len__(self):
        return len(self.items)

    def subtotal(self):
        total = 0
        for name in self.items:
            total = total + self.items[name][0] * self.items[name][1]
        return total                                       # B6: result is never rounded

    def apply_coupon(self, code):
        if code == "SAVE10":                               # B9: case-sensitive
            self.coupon = code
        elif code == "SAVE20":
            if self.subtotal() > 100:                      # B7: should be >= 100
                self.coupon = code
            else:
                raise ValueError("coupon requires a subtotal of at least 100.0")
        # B8: unknown codes are silently ignored

    def discount(self):
        if self.coupon == "SAVE10":                        # B14: minimum for SAVE20 is not
            return self.subtotal() * 0.10                  #      re-checked after items change
        if self.coupon == "SAVE20":
            return self.subtotal() * 0.20
        return 0

    def tax(self):
        return self.subtotal() * self.tax_rate             # B10: tax on price BEFORE discount

    def total(self):
        return self.subtotal() - self.discount() + self.tax()

    def average_item_price(self):
        return self.subtotal() / len(self.items)           # B11: wrong divisor, B12: crashes if empty

    def most_expensive_item(self):
        if len(self.items) == 0:
            return None
        return max(self.items, key=lambda n: self.items[n][1])   # B13: compares quantity, not price

    def receipt(self):
        lines = []
        for name in self.items:
            price = self.items[name][0]
            qty = self.items[name][1]
            lines.append(f"{name:<12}{qty:>3} x {price:>8.2f} = {price * qty:>9.2f}")
        lines.append("-" * 38)
        lines.append(f"{'Subtotal:':<28}{self.subtotal():>10.2f}")
        lines.append(f"{'Discount:':<28}{-self.discount():>10.2f}")
        lines.append(f"{'Tax:':<28}{self.tax():>10.2f}")
        lines.append(f"{'Total:':<28}{self.total():>10.2f}")
        return "\n".join(lines)
