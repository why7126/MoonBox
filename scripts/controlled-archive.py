#!/usr/bin/env python3
"""Authenticate online and use the authoritative archive coordinator."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/backend'))
from app.governance.replacement_cli import main
if __name__ == '__main__':
    raise SystemExit(main())
