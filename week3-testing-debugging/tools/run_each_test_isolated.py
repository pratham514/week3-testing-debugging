"""Run every test in its own process against the buggy module.

Because of bug B1 (shared default dict) tests contaminate each other when run
together. Running each test alone shows which tests fail because of THEIR OWN bug.

Usage: python tools/run_each_test_isolated.py
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def all_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from all_ids(item)
        else:
            yield item.id()


def main():
    suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"))
    env = dict(os.environ, CART_MODULE="cart_buggy", PYTHONDONTWRITEBYTECODE="1")
    failed = []
    ids = list(all_ids(suite))
    for test_id in ids:
        proc = subprocess.run([sys.executable, "-m", "unittest", test_id],
                              cwd=os.path.join(ROOT, "tests"), env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            failed.append(test_id.split(".", 1)[1])
    print(f"{len(failed)} of {len(ids)} tests fail against the buggy code when run in isolation:")
    for name in failed:
        print("  -", name)


if __name__ == "__main__":
    main()
