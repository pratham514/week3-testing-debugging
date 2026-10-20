"""Simple code-quality metrics (standard library only) to compare before and after.

Usage: python tools/code_metrics.py
"""
import ast
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {"BEFORE (buggy/cart_buggy.py)": "buggy/cart_buggy.py",
         "AFTER  (src/cart.py)": "src/cart.py"}
BRANCHES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp, ast.IfExp, ast.comprehension)


def analyse(path):
    source = open(os.path.join(ROOT, path), encoding="utf-8").read()
    tree = ast.parse(source)
    loc = sum(1 for l in source.splitlines() if l.strip() and not l.strip().startswith("#"))
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    documented = sum(1 for n in funcs + classes if ast.get_docstring(n))
    documented += 1 if ast.get_docstring(tree) else 0
    doc_total = len(funcs) + len(classes) + 1
    hinted = sum(1 for f in funcs if f.returns is not None)
    complexity = [1 + sum(isinstance(c, BRANCHES) for c in ast.walk(f)) for f in funcs]
    magic = 0
    for f in funcs:
        for c in ast.walk(f):
            if isinstance(c, ast.Constant) and isinstance(c.value, (int, float)) \
                    and not isinstance(c.value, bool) and c.value not in (0, 1, 2):
                magic += 1
    return {
        "Code lines (no blanks/comments)": loc,
        "Functions/methods": len(funcs),
        "Docstring coverage": f"{100 * documented // doc_total}%",
        "Functions with return type hints": f"{100 * hinted // len(funcs)}%",
        "Max cyclomatic complexity": max(complexity),
        "Average cyclomatic complexity": f"{sum(complexity) / len(complexity):.1f}",
        "Magic numbers inside functions": magic,
    }


def main():
    results = {name: analyse(path) for name, path in FILES.items()}
    names = list(results)
    print(f"{'Metric':<36}{names[0]:<32}{names[1]}")
    for metric in results[names[0]]:
        print(f"{metric:<36}{str(results[names[0]][metric]):<32}{results[names[1]][metric]}")


if __name__ == "__main__":
    main()
