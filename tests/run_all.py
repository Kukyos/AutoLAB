"""Run every smoke test; exit non-zero if any fails.

    python tests/run_all.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = [
    ["tests/template_smoke.py"],
    ["tests/solved_smoke.py"],
    ["tests/billing_smoke.py"],
    ["tests/gemini_smoke.py"],
    ["tests/api_smoke.py"],
    ["pdfedit.py"],  # its __main__ is a self-check
]

failed = []
for argv in TESTS:
    proc = subprocess.run([sys.executable, *argv], cwd=ROOT, capture_output=True, text=True)
    ok = proc.returncode == 0 and "PASS" in proc.stdout
    print(f"{'PASS' if ok else 'FAIL'}  {argv[0]}")
    if not ok:
        failed.append(argv[0])
        print((proc.stdout + proc.stderr)[-2000:])

print(f"\n{len(TESTS) - len(failed)}/{len(TESTS)} passed")
sys.exit(1 if failed else 0)
