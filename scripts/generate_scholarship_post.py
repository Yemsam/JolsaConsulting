#!/usr/bin/env python3
"""Compatibility entrypoint: collect review drafts without a paid AI service."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).with_name("collect-scholarships.mjs")
    raise SystemExit(subprocess.call(["node", str(script), *sys.argv[1:]]))
