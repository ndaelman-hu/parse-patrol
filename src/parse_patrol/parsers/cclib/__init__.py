"""
CCLib parser module initialization.
Suppresses SyntaxWarning from cclib before module imports.
"""

import warnings

# Suppress SyntaxWarning from cclib's invalid escape sequences
warnings.filterwarnings("ignore", category=SyntaxWarning, module="cclib")

import cclib  # noqa: E402, F401
