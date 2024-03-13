#!/usr/bin/env python3

import argparse

from core import BluezTarget, BluezAddressType, pair


def main():
    parser = argparse.ArgumentParser(
        prog="No interaction pairing",
        description="Try to pair to a device without user interaction",
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
    args = parser.parse_args()

    pair(BluezTarget(args.address, args.address_type), verbose=True)


if __name__ == "__main__":
    main()
