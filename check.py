#!/usr/bin/env python3
"""
check.py - the only thing in this repo that enforces anything.

Everything else here is a document that depends on you remembering it. This does not.
Wire it to a git pre-commit hook (see hooks/pre-commit) and the rules become binding.

Usage:
    python check.py              check every tracked file
    python check.py --staged     check only staged files (this is what the hook runs)
    python check.py --full       also run the template test suites (slow, not in the hook)

Exit code 0 means clean, 1 means at least one FAIL.

DESIGN NOTE, and it matters more than the code:
A checker that cries wolf gets bypassed. The first time this blocks a commit for a
reason you disagree with, you will type --no-verify, and from then on it enforces
nothing. So every check here is high-signal on purpose: it fires only on things that
are unambiguously wrong. Resist the urge to add fuzzy checks. A hook you trust and
run beats a thorough hook you route around.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".toml", ".css", ".tps", ".yml",
                 ".yaml", ".sql", ".html", ".jsx", ".js", ".mplstyle", ".example",
                 ".cfg", ".ini", ""}

# High-signal only. These match a credential's actual shape, not a word that could
# mean anything. "API_KEY" appearing in a doc is not a leak. AKIA... is.
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}",                      "AWS access key id"),
    (r"ghp_[A-Za-z0-9]{36}",                   "GitHub personal access token"),
    (r"gho_[A-Za-z0-9]{36}",                   "GitHub OAuth token"),
    (r"github_pat_[A-Za-z0-9_]{60,}",          "GitHub fine-grained token"),
    (r"sk-ant-[A-Za-z0-9\-_]{20,}",            "Anthropic API key"),
    (r"sk-[A-Za-z0-9]{40,}",                   "OpenAI-style API key"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}",         "Slack token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----",    "private key block"),
    (r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}", "JWT"),
    (r"postgres(?:ql)?://[^\s:@]+:[^\s:@]+@",  "Postgres URL with inline password"),
    (r"AIza[0-9A-Za-z\-_]{35}",                "Google API key"),
]

# A file whose whole job is to show placeholders is not a leak.
SECRET_SKIP = {".env.example", "check.py"}

NEVER_TRACK = [
    (re.compile(r"(^|/)\.env$"),            ".env must never be tracked"),
    (re.compile(r"(^|/)__pycache__/"),      "__pycache__ must never be tracked"),
    (re.compile(r"\.pyc$"),                 "compiled python must never be tracked"),
    (re.compile(r"(^|/)\.venv/"),           ".venv must never be tracked"),
    (re.compile(r"(^|/)data/raw/"),         "raw data must never be tracked"),
    (re.compile(r"\.bak$"),                 "backup files must never be tracked"),
]

fails = []
warns = []
checked = 0


def fail(path, msg):
    fails.append(f"FAIL  {path}: {msg}")


def warn(path, msg):
    warns.append(f"warn  {path}: {msg}")


def git(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.splitlines()


def files_to_check(staged):
    if staged:
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACM")
    else:
        names = git("ls-files")
    return [ROOT / n for n in names if (ROOT / n).is_file()]


def check_tracked_paths(staged):
    names = (git("diff", "--cached", "--name-only") if staged else git("ls-files"))
    for n in names:
        for pat, msg in NEVER_TRACK:
            if pat.search(n):
                fail(n, msg + "  (fix: git rm -r --cached <path>)")


def check_text(path):
    global checked
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    try:
        raw = path.read_bytes()
    except OSError:
        return
    if b"\x00" in raw[:4096]:
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(path.relative_to(ROOT), "not valid UTF-8")
        return

    checked += 1
    rel = path.relative_to(ROOT)

    if raw.startswith(b"\xef\xbb\xbf"):
        fail(rel, "UTF-8 BOM present, files must be written without one")

    for i, line in enumerate(text.splitlines(), 1):
        if "\u2014" in line:
            fail(rel, f"line {i}: em-dash. Use a comma, a period, or parentheses")
        if "\u2013" in line:
            fail(rel, f"line {i}: en-dash")

    if path.name not in SECRET_SKIP:
        for pat, label in SECRET_PATTERNS:
            m = re.search(pat, text)
            if m:
                fail(rel, f"looks like a {label}. If this is real, rotate the key. "
                          f"Removing the commit does not un-expose it")

    if path.suffix == ".py":
        try:
            compile(text, str(path), "exec")
        except SyntaxError as e:
            fail(rel, f"python syntax error, line {e.lineno}: {e.msg}")

    if path.suffix == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            fail(rel, f"invalid JSON: {e}")

    if path.suffix == ".toml":
        try:
            import tomllib
            tomllib.loads(text)
        except ImportError:
            pass
        except Exception as e:
            fail(rel, f"invalid TOML: {e}")

    if path.suffix == ".tps":
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(text)
        except Exception as e:
            fail(rel, f"invalid XML: {e}")


def check_pins(path):
    """An unpinned dependency is how a working deploy breaks with no commit."""
    if path.name != "requirements.txt":
        return
    rel = path.relative_to(ROOT)
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.split("#")[0].strip()
        if not s:
            continue
        if "==" not in s:
            warn(rel, f"line {i}: '{s}' is not pinned to an exact version")


def run_tests():
    print("\nrunning template tests (--full)")
    svc = ROOT / "templates" / "flask-service"
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=svc,
                       capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[-400:])
    if r.returncode != 0:
        fail("templates/flask-service", "test suite failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true", help="only staged files (hook mode)")
    ap.add_argument("--full", action="store_true", help="also run template tests")
    args = ap.parse_args()

    check_tracked_paths(args.staged)
    for f in files_to_check(args.staged):
        check_text(f)
        check_pins(f)
    if args.full:
        run_tests()

    scope = "staged files" if args.staged else "all tracked files"
    print(f"checked {checked} text files ({scope})")

    for w in warns:
        print(w)
    if fails:
        print()
        for f in fails:
            print(f)
        print(f"\n{len(fails)} problem(s). Commit blocked.")
        print("Override with --no-verify only if you know why. If you are doing that")
        print("routinely, the check is wrong and should be fixed, not bypassed.")
        return 1

    print("clean" + (f", {len(warns)} warning(s)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
