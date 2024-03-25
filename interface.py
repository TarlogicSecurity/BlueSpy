#!/usr/bin/env python3

"""
Logging and text interface related code.
"""


class bcolors:
    HEADER = "\033[34m"
    OK_BLUE = "\033[94m"
    OK_CYAN = "\033[96m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class loglevel:
    INFO = ("I", bcolors.OK_GREEN)
    WARN = ("!", bcolors.WARNING)
    INPUT = ("?", bcolors.OK_BLUE)
    DEBUG = ("D", bcolors.OK_BLUE)


def color_print(color: bcolors, msg: str):
    """
    Print a string with the selected color.
    """
    print(f"{color}{msg}{bcolors.ENDC}")


def log(level: loglevel, msg: str):
    """
    Print a string with the selected log level.
    """
    print(f"[{level[1]}{level[0]}{bcolors.ENDC}] {msg}")


def log_info(msg: str):
    """
    Print an info string.
    """
    log(loglevel.INFO, msg)


def log_warn(msg: str):
    """
    Print a warning string.
    """
    log(loglevel.WARN, msg)


def input_yn(msg: str) -> bool:
    """
    Get a yes/no answer to a prompt.
    """
    log(loglevel.INPUT, msg)
    option = input("[Y/n] ") or "y"
    return option.lower() in ("y", "yes")
