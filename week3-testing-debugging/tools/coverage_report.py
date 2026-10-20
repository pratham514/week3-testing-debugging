"""Line coverage of src/cart.py using only the standard library.

Usage: python tools/coverage_report.py
(If you prefer the popular tool:  pip install coverage
                                  coverage run -m unittest discover tests
                                  coverage report -m )
"""
import os
import sys
import trace
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "src", "cart.py")


def main():
    def run_all():
        # Discovery imports src/cart.py, so it must happen while tracing is on.
        suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"))
        return unittest.TextTestRunner(stream=open(os.devnull, "w")).run(suite)

    tracer = trace.Trace(count=1, trace=0)
    result = tracer.runfunc(run_all)
    executable = set(trace._find_executable_linenos(TARGET)) - {0}  # line 0 is a tracer artefact
    hit = {line for (path, line), n in tracer.results().counts.items()
           if os.path.abspath(path) == TARGET}
    covered = executable & hit
    missed = sorted(executable - hit)
    pct = 100 * len(covered) / len(executable)
    print(f"Tests run: {result.testsRun}, failures: {len(result.failures) + len(result.errors)}")
    print(f"File: src/cart.py")
    print(f"Executable lines: {len(executable)}   Covered: {len(covered)}   Missed: {len(missed)}")
    print(f"Line coverage: {pct:.1f}%")
    if missed:
        print("Missed lines:", missed)


if __name__ == "__main__":
    main()
