"""
Streamlit Workstation UI Entrypoint (Root Wrapper)
==================================================
Delegates execution to src.ui_frontend.app
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Execute modern workstation UI
from src.ui_frontend.app import *
