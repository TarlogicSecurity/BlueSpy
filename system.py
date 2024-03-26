#!/usr/bin/env python3

"""
This module contains functions to interact with system programs.
"""

from typing import Callable, List
import subprocess


class CommandValidationException(Exception):
    def __init__(self, command, output) -> None:
        self.output = output
        super().__init__(f'Error while executing command "{command}"', output)


def run_and_check(
    command: List[str],
    is_valid: Callable[[str], bool] = lambda _: True,
    verbose: bool = False,
) -> None:
    """
    Run a system program and capture the output.
    You may validate that the command has executed correctly with a validation function.
    On exception, the output of the failed command is shown.
    """
    if verbose:
        print("[C] " + " ".join(command))
    output = subprocess.run(command, capture_output=True)
    out = output.stdout.decode("utf-8")
    if verbose:
        print(out)
    if not is_valid(out) or output.stderr != b"":
        cmdline = " ".join(command)
        raise CommandValidationException(cmdline, out)


def check_command_available(command: str) -> bool:
    """
    Check wether a command or tool is available in the system.
    """
    output = subprocess.run(command, capture_output=True)
    return output.returncode == 0
