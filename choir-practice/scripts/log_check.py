#!/usr/bin/env python3
"""Record a manual check (e.g. proofreading passes, metadata approval) in WORK/checks.jsonl.

  python3 log_check.py WORK <phase 0-6> <check-id> <pass|fail|warn|manual> "note in the user's language"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log_check
if len(sys.argv) < 5: sys.exit(__doc__)
log_check(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else '')
print('logged')
