"""
Development Bootstrap Script (Root Compatibility Wrapper)
==========================================================
Re-exports and runs scripts/bootstrap_dev.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scripts.bootstrap_dev import main

if __name__ == "__main__":
    main()
