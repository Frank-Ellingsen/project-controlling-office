"""
Streamlit Executive UI (v2 Entrypoint Wrapper)
==============================================
Delegates execution to src.ui_frontend.app
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui_frontend.app import *
