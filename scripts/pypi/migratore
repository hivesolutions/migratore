#!/bin/sh
# -*- coding: utf-8 -*-

# sets the temporary variables
USR_BIN_PATH=/usr/bin
PYTHON_PATH=$USR_BIN_PATH/python
SCRIPT_NAME=migratore_pypi.py

# retrieves the script directory path
SCRIPT_DIRECTORY_PATH=$(dirname $(readlink $0 || echo $0))

# executes the initial python script with
# the provided arguments
$PYTHON_PATH "$SCRIPT_DIRECTORY_PATH/$SCRIPT_NAME" "$@"

# exits the process
exit $?
