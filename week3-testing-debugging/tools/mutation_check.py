"""Check that the tests detect each known bug.

For every bug B0-B14, the original flaw is re-introduced (alone) into a copy of
the fixed module. The test-suite is then run. If at least one test fails, the
bug is "detected". Detection rate = detected bugs / total bugs.

Usage: python tools/mutation_check.py
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, "src", "cart.py"), encoding="utf-8").read()

# (id, description, [(old text, new text), ...])
MUTANTS = [
    ("B0", "syntax error: missing colon after add_item signature",
     [("def add_item(self, name: str, price: float, quantity: int = 1) -> None:",
       "def add_item(self, name: str, price: float, quantity: int = 1) -> None")]),
    ("B1", "mutable default argument shares items between carts",
     [("def __init__(self, tax_rate: float = TAX_RATE) -> None:",
       "def __init__(self, tax_rate: float = TAX_RATE, items: dict = {}) -> None:"),
      ("self._items: Dict[str, CartItem] = {}", "self._items = items")]),
    ("B2", "adding an existing item overwrites quantity",
     [("item.quantity += quantity", "item.quantity = quantity")]),
    ("B3", "price 0 accepted (< instead of <=)",
     [("if price <= 0:", "if price < 0:")]),
    ("B4", "quantity never validated",
     [("if not isinstance(quantity, int) or quantity <= 0:", "if False:")]),
    ("B5", "remove_item leaves quantity 0 and allows over-removal",
     [("""        if quantity > current:
            raise ValueError("cannot remove more than is in the cart")
        if quantity == current:
            del self._items[name]
        else:
            self._items[name].quantity = current - quantity""",
       """        self._items[name].quantity = current - quantity
        if self._items[name].quantity < 0:
            del self._items[name]""")]),
    ("B6", "subtotal not rounded",
     [("subtotal = round(sum(i.line_total for i in self._items.values()), 2)",
       "subtotal = sum(i.line_total for i in self._items.values())")]),
    ("B7", "SAVE20 boundary: > 100 instead of >= 100",
     [("if self.subtotal() < minimum:\n            raise", "if self.subtotal() <= minimum:\n            raise")]),
    ("B8", "unknown coupon silently ignored",
     [('raise ValueError("unknown coupon")', "return")]),
    ("B9", "coupon code is case-sensitive",
     [("code = code.strip().upper()", "code = code.strip()")]),
    ("B10", "tax charged before discount",
     [("tax = round(taxable * self.tax_rate, 2)", "tax = round(subtotal * self.tax_rate, 2)")]),
    ("B11", "average divides by distinct items, not units",
     [("units = self.total_quantity()", "units = len(self._items)")]),
    ("B12", "average crashes on empty cart",
     [("        if units == 0:\n            return 0.0\n", "")]),
    ("B13", "most_expensive_item compares quantity",
     [("key=lambda n: self._items[n].price", "key=lambda n: self._items[n].quantity")]),
    ("B14", "coupon minimum not re-checked after items change",
     [("        if subtotal < minimum:\n            return 0.0\n        return round(subtotal * rate, 2)",
       "        return round(subtotal * rate, 2)")]),
]


def run_tests(module_dir, module_name):
    env = dict(os.environ, CART_MODULE=module_name, PYTHONPATH=module_dir,
               PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                          cwd=ROOT, env=env, capture_output=True, text=True)
    return proc.returncode, proc.stderr


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # Baseline: the unmodified fixed code must pass every test.
        open(os.path.join(tmp, "cart_mutant.py"), "w", encoding="utf-8").write(SRC)
        code, _ = run_tests(tmp, "cart_mutant")
        print("Baseline (fixed code):", "all tests pass" if code == 0 else "TESTS FAIL")
        print()
        print(f"{'Bug':<5}{'Result':<10}{'Failing tests':<15}Description")
        detected = 0
        for bug_id, desc, edits in MUTANTS:
            mutated = SRC
            for old, new in edits:
                assert mutated.count(old) == 1, f"{bug_id}: pattern not found exactly once"
                mutated = mutated.replace(old, new)
            open(os.path.join(tmp, "cart_mutant.py"), "w", encoding="utf-8").write(mutated)
            code, err = run_tests(tmp, "cart_mutant")
            failing = err.count("\nFAIL:") + err.count("\nERROR:")
            killed = code != 0
            detected += killed
            print(f"{bug_id:<5}{'DETECTED' if killed else 'MISSED':<10}{failing:<15}{desc}")
        print()
        print(f"Detected {detected} of {len(MUTANTS)} bugs "
              f"= {100 * detected / len(MUTANTS):.0f}% (target: at least 80%)")


if __name__ == "__main__":
    main()
