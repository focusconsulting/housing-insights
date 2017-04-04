#!/bin/bash

# data.sh -- wrapper around data.py so imports work
#            without ghetto wizardry.
#
# Dependencies: 
#   Needs the realpath utility installed.

# Allow us to use relative paths.
BINDIR="$( dirname $0 )"
cd "${BINDIR}"
cd ..

# Find our python path so our other script will work.
PYPATH=".:$( realpath .. )"

# Call data.py with shell magic.
PYTHONPATH="${PYPATH}" env/bin/python cmd/data.py "$@"
