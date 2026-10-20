# Week 3: Software Testing and Debugging Exercise

A small shopping-cart module that was written with **15 deliberate bugs** (one syntax error and 14 logic/runtime bugs). The project contains the buggy original, 39 unit tests that detect the bugs, a record of the debugging sessions, the fixed and refactored code, and a debugging report.

## Results at a glance

| Measure | Result |
|---|---|
| Unit tests | 39 |
| Tests passing on the original buggy code | 9 of 39 (30 fail) |
| Tests passing on the fixed code | 39 of 39 |
| Bugs detected by the tests | 15 of 15 (100%, target 80%) |
| Line coverage of `src/cart.py` | 100% |
| Docstring coverage (before / after) | 0% / 95% |
| Return type hints (before / after) | 0% / 100% |

## Project structure

```
week3-testing-debugging/
├── buggy/
│   ├── cart_syntax_error.py   # first draft with syntax error B0
│   └── cart_buggy.py          # original code with logic bugs B1-B14 (each bug is commented)
├── src/
│   └── cart.py                # fixed and refactored code
├── tests/
│   └── test_cart.py           # 39 unit tests
├── tools/
│   ├── run_against_buggy.py        # run the tests on the buggy code
│   ├── run_each_test_isolated.py   # run each test alone on the buggy code
│   ├── mutation_check.py           # re-introduce each bug and check the tests catch it
│   ├── coverage_report.py          # line coverage (standard library only)
│   ├── code_metrics.py             # before/after code-quality metrics
│   ├── benchmark.py                # before/after timing
│   └── repro_b1.py, repro_b2.py, repro_b10.py   # small scripts used for pdb sessions
├── docs/
│   ├── Debugging_Report.docx  # full debugging report
│   ├── debug_sessions/        # real pdb transcripts
│   ├── results/               # real output of every tool above
│   └── diagrams/              # architecture, workflow and results diagrams
├── requirements.txt
└── README.md
```

## Requirements

Python 3.8 or newer. No third-party packages.

## Installation

```bash
git clone https://github.com/pratham514/week3-testing-debugging.git
cd week3-testing-debugging
```

## Usage

Run the tests on the **fixed** code (all 39 pass):

```bash
python -m unittest discover -s tests -v
```

Run the same tests on the **original buggy** code (30 fail, which is the point):

```bash
python tools/run_against_buggy.py
```

Check that the tests detect every bug (re-introduces each bug one at a time):

```bash
python tools/mutation_check.py
```

Line coverage, code metrics and benchmark:

```bash
python tools/coverage_report.py
python tools/code_metrics.py
python tools/benchmark.py
```

Repeat a debugging session yourself (step through bug B2 with `pdb`):

```bash
python -m pdb tools/repro_b2.py
(Pdb) break buggy/cart_buggy.py:16
(Pdb) continue
(Pdb) p self.items
```

Optional: if you have the `coverage` package, `coverage run -m unittest discover tests` then `coverage report -m` gives the same information.

## The module under test

`ShoppingCart` supports `add_item`, `remove_item`, `subtotal`, `apply_coupon`, `discount`, `tax`, `total`, `average_item_price`, `most_expensive_item` and `receipt`.

Rules: prices must be above 0, quantities must be positive whole numbers, money is rounded to 2 decimals, `SAVE10` gives 10% off, `SAVE20` gives 20% off when the subtotal is at least 100.00, coupon codes are case-insensitive, and tax (8% by default) is charged after the discount.

## The bugs

| ID | Type | Short description |
|----|------|-------------------|
| B0 | Syntax | Missing colon after a function signature |
| B1 | State | Mutable default argument shares items between carts |
| B2 | Logic | Adding an existing item overwrites its quantity |
| B3 | Boundary | Price 0 accepted (`<` instead of `<=`) |
| B4 | Validation | Quantity never validated |
| B5 | Logic | Removing leaves quantity 0 and over-removal is silently allowed |
| B6 | Numeric | Subtotal not rounded (0.1 + 0.2 = 0.30000000000000004) |
| B7 | Boundary | SAVE20 rejected at exactly 100.00 (`>` instead of `>=`) |
| B8 | Error handling | Unknown coupon silently ignored |
| B9 | Input | Coupon code is case-sensitive |
| B10 | Logic | Tax charged before the discount |
| B11 | Logic | Average divides by distinct items instead of units |
| B12 | Runtime | Average crashes on an empty cart (ZeroDivisionError) |
| B13 | Logic | Most expensive item compares quantity instead of price |
| B14 | State | Coupon minimum not re-checked after items are removed |

The full explanation of each bug, how it was found and how it was fixed is in `docs/Debugging_Report.docx`.

## Author

Pratham
