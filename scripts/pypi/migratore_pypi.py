#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import migratore

if __name__ == "__main__":
    # validates that the provided number of arguments
    # is the expected one, in case it's not raises a
    # runtime error indicating the problem
    if len(sys.argv) < 2: raise RuntimeError("Invalid number of arguments")

    # retrieves the fir
    scope = sys.argv[1]

    # retrieves the set of extra arguments to be sent to the
    # command to be executed, (this may be dangerous)
    args =  sys.argv[2:]

    # retrieves both the loader command for the current
    # scope and then uses it to execute the command with
    # the extra arguments as the passing value
    is_command = hasattr(migratore, "run_" + scope)
    if is_command: command = getattr(migratore, "run_" + scope)
    else: command = getattr(migratore, scope)
    command(*args)
