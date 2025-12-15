"""
Pytest configuration for unit tests.
Sets up sys.argv before any application imports.
"""

# IMPORTANT: Set up sys.argv BEFORE any application imports to prevent
# ValueError in application/__init__.py which parses sys.argv at import time
import sys
if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    sys.argv = ['pytest', '5000', 'test-auth-key']
