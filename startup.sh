#!/bin/bash
# startup.sh
# Set up the virtual environment and Python path for non-interactive,
# non-login shells.

# Activate virtual environment
source /home/surge/venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="/home/surge/surge/buildpy/src/surge-python/:$PYTHONPATH"

# Execute Python script
exec "$@"
