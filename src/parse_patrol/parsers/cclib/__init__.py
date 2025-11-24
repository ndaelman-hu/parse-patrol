"""
CCLib parser module initialization.
Suppresses SyntaxWarning from cclib before module imports.
"""

import warnings
import importlib

# Suppress SyntaxWarning from cclib's invalid escape sequences
warnings.filterwarnings("ignore", category=SyntaxWarning, module="cclib")

# Explicitly import the external cclib package to avoid self-import
external_cclib = importlib.import_module("cclib")

__all__ = ["external_cclib"]
