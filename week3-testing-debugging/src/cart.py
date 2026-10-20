"""Shopping cart module (fixed and refactored version).

Money values are rounded to 2 decimals. Coupons:
    SAVE10 - 10% off, any subtotal
    SAVE20 - 20% off, subtotal must be at least 100.00
Tax is charged on the price AFTER the discount.
"""
from dataclasses import dataclass
from typing import Dict, Optional

TAX_RATE = 0.08
# coupon code -> (discount rate, minimum subtotal required)
COUPONS = {"SAVE10": (0.10, 0.0), "SAVE20": (0.20, 100.0)}


@dataclass
class CartItem:
    """One line in the cart."""
    price: float
    quantity: int

    @property
    def line_total(self) -> float:
        """Price multiplied by quantity."""
        return self.price * self.quantity


@dataclass
class Summary:
    """All money amounts for the cart, calculated in a single pass."""
    subtotal: float
    discount: float
    tax: float
    total: float


class ShoppingCart:
    """A shopping cart with coupons and tax."""

    def __init__(self, tax_rate: float = TAX_RATE) -> None:
        self.tax_rate = tax_rate
        self._items: Dict[str, CartItem] = {}
        self._coupon: Optional[str] = None

    # ---- validation helpers ---------------------------------------------
    @staticmethod
    def _check_price(price: float) -> None:
        """Reject prices that are zero or negative."""
        if price <= 0:
            raise ValueError("price must be greater than 0")

    @staticmethod
    def _check_quantity(quantity: int) -> None:
        """Reject quantities that are not positive whole numbers."""
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")

    # ---- items ----------------------------------------------------------
    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """Add an item; adding an existing item increases its quantity."""
        self._check_price(price)
        self._check_quantity(quantity)
        item = self._items.get(name)
        if item:
            item.quantity += quantity
        else:
            self._items[name] = CartItem(price, quantity)

    def remove_item(self, name: str, quantity: Optional[int] = None) -> None:
        """Remove `quantity` units, or the whole item if quantity is None."""
        if name not in self._items:
            raise KeyError(name)
        if quantity is None:
            del self._items[name]
            return
        self._check_quantity(quantity)
        current = self._items[name].quantity
        if quantity > current:
            raise ValueError("cannot remove more than is in the cart")
        if quantity == current:
            del self._items[name]
        else:
            self._items[name].quantity = current - quantity

    def quantity_of(self, name: str) -> int:
        """Quantity of one item in the cart (0 if absent)."""
        item = self._items.get(name)
        return item.quantity if item else 0

    def total_quantity(self) -> int:
        """Number of units in the cart across all items."""
        return sum(item.quantity for item in self._items.values())

    def __len__(self) -> int:
        """Number of distinct items in the cart."""
        return len(self._items)

    # ---- coupons and money ----------------------------------------------
    def apply_coupon(self, code: str) -> None:
        """Apply a coupon (case-insensitive). Only one coupon is active at a time."""
        code = code.strip().upper()
        if code not in COUPONS:
            raise ValueError("unknown coupon")
        _, minimum = COUPONS[code]
        if self.subtotal() < minimum:
            raise ValueError(f"coupon requires a subtotal of at least {minimum}")
        self._coupon = code

    def _discount_for(self, subtotal: float) -> float:
        """Discount for a subtotal; 0 if no coupon or its minimum is not met."""
        if self._coupon is None:
            return 0.0
        rate, minimum = COUPONS[self._coupon]
        if subtotal < minimum:
            return 0.0
        return round(subtotal * rate, 2)

    def summary(self) -> Summary:
        """Calculate subtotal, discount, tax and total once."""
        subtotal = round(sum(i.line_total for i in self._items.values()), 2)
        discount = self._discount_for(subtotal)
        taxable = subtotal - discount
        tax = round(taxable * self.tax_rate, 2)
        total = round(taxable + tax, 2)
        return Summary(subtotal, discount, tax, total)

    def subtotal(self) -> float:
        """Sum of all line totals, rounded to 2 decimals."""
        return self.summary().subtotal

    def discount(self) -> float:
        """Current coupon discount."""
        return self.summary().discount

    def tax(self) -> float:
        """Tax on the discounted subtotal."""
        return self.summary().tax

    def total(self) -> float:
        """Amount to pay: discounted subtotal plus tax."""
        return self.summary().total

    # ---- statistics -----------------------------------------------------
    def average_item_price(self) -> float:
        """Average price per unit in the cart (0.0 for an empty cart)."""
        units = self.total_quantity()
        if units == 0:
            return 0.0
        return round(self.subtotal() / units, 2)

    def most_expensive_item(self) -> Optional[str]:
        """Name of the item with the highest unit price, or None."""
        if not self._items:
            return None
        return max(self._items, key=lambda n: self._items[n].price)

    # ---- output ---------------------------------------------------------
    def receipt(self) -> str:
        """Plain-text receipt."""
        s = self.summary()
        lines = [
            f"{name:<12}{i.quantity:>3} x {i.price:>8.2f} = {i.line_total:>9.2f}"
            for name, i in self._items.items()
        ]
        lines.append("-" * 38)
        lines.append(f"{'Subtotal:':<28}{s.subtotal:>10.2f}")
        lines.append(f"{'Discount:':<28}{-s.discount:>10.2f}")
        lines.append(f"{'Tax:':<28}{s.tax:>10.2f}")
        lines.append(f"{'Total:':<28}{s.total:>10.2f}")
        return "\n".join(lines)
