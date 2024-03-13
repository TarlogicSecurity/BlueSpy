from enum import Enum
from typing import Callable, List
import subprocess
import re
import shlex
from enum import Enum


class BluezAddressType(Enum):
    BR_EDR = 0
    LE_PUBLIC = 1
    LE_RANDOM = 2

    def __str__(self):
        return self.name


def is_valid_bluezaddress(address: str) -> bool:
    ok = True
    try:
        Address(address)
    except ValueError:
        ok = False

    return ok


class Address:
    regexp = re.compile(r"(?i:^([\da-f]{2}:){5}[\da-f]{2}$)")

    def __init__(self, value: str):
        if self.regexp.match(value) is None:
            raise ValueError(f"{value} is not a valid bluetooth address")
        self._address = value.lower()

    def __str__(self):
        return self._address

    def __eq__(self, other):
        return self._address == str(other).lower()


class BluezTarget:
    regexp = re.compile(r"(?i:^([\da-f]{2}:){5}[\da-f]{2}$)")

    def __init__(
        self, address: str, type: int | BluezAddressType = BluezAddressType.BR_EDR
    ):
        self.address = Address(address)
        if isinstance(type, int):
            type = BluezAddressType(type)
        elif isinstance(type, str):
            type = BluezAddressType(int(type))
        self.type = type

    def __eq__(self, other):
        return self.address == other.address and self.type == other.type


def run_and_check(
    command: List[str],
    is_valid: Callable[[str], bool] = lambda _: True,
    verbose: bool = False,
) -> None:
    if verbose:
        print("[C] " + " ".join(command))
    output = subprocess.run(command, capture_output=True)
    out = output.stdout.decode("utf-8")
    if verbose:
        print(out)
    if not is_valid(out) or output.stderr != b"":
        cmdline = " ".join(command)
        raise Exception(f"Error while executing command {cmdline}", out)


class BluezIoCaps(Enum):
    DisplayOnly = 0
    DisplayYesNo = 1
    KeyboardOnly = 2
    NoInputNoOutput = 3
    KeyboardDisplay = 4


def pair(target: BluezTarget, verbose: bool = False) -> None:
    # Configure ourselves to be bondable and pairable
    run_and_check(shlex.split("sudo btmgmt bondable true"), verbose=verbose)
    run_and_check(shlex.split("sudo btmgmt pairable true"), verbose=verbose)

    # No need for link security ;)
    run_and_check(shlex.split("sudo btmgmt linksec false"), verbose=verbose)

    # Try to pair to a device with NoInputNoOutput capabilities
    # TODO: Sometimes this may fail due to agent requesting user confirmation.
    # Registering the following agent may help: "yes | bt-agent -c NoInputNoOutput"
    run_and_check(
        shlex.split(
            f"sudo btmgmt pair -c {str(BluezIoCaps.NoInputNoOutput.value)} -t {str(target.type.value)} {str(target.address)}"
        ),
        is_valid=lambda out: not ("failed" in out and not "Already Paired" in out),
        verbose=verbose,
    )


def connect(target: BluezTarget, timeout: int = 2, verbose: bool = False):
    run_and_check(
        shlex.split(f"bluetoothctl --timeout {str(timeout)} scan on"), verbose=verbose
    )
    run_and_check(
        shlex.split(f"bluetoothctl connect {str(target.address)}"), verbose=verbose
    )


def normalize_address(target: BluezTarget) -> str:
    return str(target.address).upper().replace(":", "_")


def to_card_name(target: BluezTarget) -> str:
    return "bluez_card." + normalize_address(target=target)


def to_source_name(target: BluezTarget) -> str:
    return "bluez_input." + normalize_address(target=target) + ".0"


def record(target: BluezTarget, outfile: str, verbose: bool = True):
    source_name = to_source_name(target)
    card_name = to_card_name(target)
    run_and_check(
        shlex.split(f"pactl set-card-profile {card_name} headset-head-unit-msbc"),
        verbose=verbose,
    )
    try:
        run_and_check(["parecord", "-d", source_name, outfile], verbose=verbose)
    except KeyboardInterrupt:
        pass
    except:
        raise


def playback(sink: str, file: str, verbose: bool = True):
    run_and_check(["paplay", "-d", sink, file], verbose=verbose)
