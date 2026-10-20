"""Compare how long receipt() takes in the buggy and fixed versions.

Usage: python tools/benchmark.py
"""
import os
import sys
import timeit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "buggy"))
import cart            # fixed
import cart_buggy      # original

ITEMS, REPEATS = 2000, 50


def build(cart_class, **kwargs):
    c = cart_class(**kwargs)
    for i in range(ITEMS):
        c.add_item(f"item{i}", 1.5 + i % 7, 1 + i % 3)
    return c


old = build(cart_buggy.ShoppingCart, items={})   # pass a fresh dict to avoid bug B1
new = build(cart.ShoppingCart)
for label, name in (("receipt()", "receipt"), ("total()", "total")):
    t_old = min(timeit.repeat(getattr(old, name), number=REPEATS, repeat=5))
    t_new = min(timeit.repeat(getattr(new, name), number=REPEATS, repeat=5))
    print(f"{label} with {ITEMS} items, {REPEATS} calls (best of 5)")
    print(f"  before (buggy): {t_old:.3f} s")
    print(f"  after  (fixed): {t_new:.3f} s")
    print(f"  speed-up: {t_old / t_new:.1f}x")
