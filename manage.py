#!/usr/bin/env python3

from dev.utilities import process_cli, help, CommandException
import sys

try:
    process_cli(sys.argv[1:])
except CommandException:
    help()
except Exception as e:
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__)
