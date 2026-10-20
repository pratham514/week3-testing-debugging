"""Run the unit tests against the ORIGINAL buggy module (buggy/cart_buggy.py).

Usage: python tools/run_against_buggy.py
Expect many failures - that is the point: the tests detect the bugs.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = dict(os.environ, CART_MODULE="cart_buggy")
sys.exit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                         cwd=ROOT, env=env))
