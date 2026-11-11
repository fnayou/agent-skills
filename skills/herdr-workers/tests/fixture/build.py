#!/usr/bin/env python3
"""Build the throwaway git repository the scenarios run against.

Usage: python3 skills/herdr-workers/tests/fixture/build.py <target-directory>

The target must not exist yet, or be empty. The content is fixed, so every
scenario starts from the same state: one commit on main, one failing test,
one typo in the README, six old notes and twelve unsorted documents.
"""
import subprocess
import sys
from pathlib import Path

FILES = {
    ".gitignore": "__pycache__/\n",
    "README.md": (
        "# calc\n"
        "\n"
        "A tiny library used as a test fixture.\n"
        "\n"
        "Version: 0.1.0\n"
        "\n"
        "The functions recieve numbers and return numbers.\n"
    ),
    "calc/__init__.py": "",
    "calc/core.py": (
        '"""Arithmetic helpers."""\n'
        "\n"
        "\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "\n"
        "def mean(values):\n"
        "    return sum(values) / (len(values) + 1)\n"
    ),
    "tests/__init__.py": "",
    "tests/test_core.py": (
        "import unittest\n"
        "\n"
        "from calc.core import add, mean\n"
        "\n"
        "\n"
        "class CoreTest(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        self.assertEqual(add(2, 3), 5)\n"
        "\n"
        "    def test_mean(self):\n"
        "        self.assertEqual(mean([2, 4, 6]), 4)\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    unittest.main()\n"
    ),
}
FILES.update({f"notes/old-{n}.txt": f"old note {n}\n" for n in range(1, 7)})

# Twelve documents to sort by content: four invoices, four letters, four
# reports, in no order. skills/herdr-workers/tests/check.py holds the same answer key.
INBOX = {
    1: ("letter", "Dear Ms Ortega,\n\nThank you for your visit last week. We will write again in May.\n\nKind regards,\nP. Lind\n"),
    2: ("invoice", "Invoice 2031\n\nTwo chairs, oak: 240.00 EUR\nAmount due: 240.00 EUR, payable within 30 days.\n"),
    3: ("report", "Quarterly report, Q1\n\nSales rose by 4 percent. Returns fell. Two shops opened.\n"),
    4: ("invoice", "Invoice 2032\n\nDelivery, zone B: 35.00 EUR\nAmount due: 35.00 EUR, payable within 30 days.\n"),
    5: ("report", "Monthly report, March\n\nThe warehouse handled 1,200 parcels. No accident was recorded.\n"),
    6: ("letter", "Dear Mr Abara,\n\nWe were sorry to hear about the delay. Please accept our apologies.\n\nYours sincerely,\nD. Roy\n"),
    7: ("report", "Annual report, summary\n\nRevenue grew for the third year. Staff numbers stayed level.\n"),
    8: ("letter", "Dear Dr Senn,\n\nI would like to invite you to our open day on 12 June.\n\nBest wishes,\nA. Kovac\n"),
    9: ("invoice", "Invoice 2033\n\nRepair of one table: 80.00 EUR\nAmount due: 80.00 EUR, payable within 30 days.\n"),
    10: ("letter", "Dear Mrs Hale,\n\nYour order has arrived at the shop. You may collect it any weekday.\n\nKind regards,\nP. Lind\n"),
    11: ("invoice", "Invoice 2034\n\nSix cushions: 90.00 EUR\nAmount due: 90.00 EUR, payable within 30 days.\n"),
    12: ("report", "Weekly report, week 14\n\nThree deliveries were late. The cause was a closed road.\n"),
}
FILES.update({f"inbox/doc-{n:02}.txt": text for n, (_, text) in INBOX.items()})


def git(target, *args):
    subprocess.run(["git", "-C", str(target), *args], check=True, capture_output=True, text=True)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    target = Path(sys.argv[1]).resolve()
    if target.exists() and any(target.iterdir()):
        sys.exit(f"ERROR target is not empty: {target}")
    for name, content in FILES.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git(target, "init", "-b", "main")
    git(target, "add", "-A")
    git(target, "-c", "commit.gpgsign=false", "commit", "-m", "chore: fixture")
    print("FIXTURE", target)


if __name__ == "__main__":
    main()
