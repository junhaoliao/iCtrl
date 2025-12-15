#!/usr/bin/env python
"""
Wrapper script to run the iCtrl server with coverage collection.
Handles SIGTERM gracefully to ensure coverage data is written.

Usage:
  python run_with_coverage.py <port> <auth_key>  # runs ictrl_be.main() (local mode)
"""
import atexit
import os
import sys
import signal
import coverage

# Start coverage before importing application code
data_file = os.environ.get('COVERAGE_FILE', '/coverage/.coverage')
cov = coverage.Coverage(
    data_file=data_file,
    config_file='pyproject.toml',
)
cov.start()


def save_coverage():
    """Save coverage data on exit."""
    print(f"\nSaving coverage data to {data_file}...")
    cov.stop()
    cov.save()
    print("Coverage data saved.")


# Register atexit handler
atexit.register(save_coverage)


def signal_handler(signum, frame):
    """Handle termination signals to exit gracefully."""
    print(f"\nReceived signal {signum}, shutting down...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    # Import and run the entry point from ictrl_be.py
    from ictrl_be import main
    main()
