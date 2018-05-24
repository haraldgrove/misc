#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Harald Grove"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import time
import sys
import random


def countkmer(s, k0, k1):
    low = False
    high = True
    db = {}
    for ind in range(0, len(s) - k0):
        km = s[ind : ind + k0]
        db[km] = db.get(km, 0) + 1
    for key, val in db.items():
        if val > 3:
            low = True
    db = {}
    for ind in range(0, len(s) - k1):
        km = s[ind : ind + k1]
        db[km] = db.get(km, 0) + 1
    for key, val in db.items():
        if val > 1:
            high = False
            break
    return low and high


def printkmer(s, k0, k1):
    db = {}
    print(s)
    for ind in range(0, len(s) - k0):
        km = s[ind : ind + k0]
        db[km] = db.get(km, 0) + 1
    for key, val in db.items():
        print(key, val)
    db = {}
    for ind in range(0, len(s) - k1):
        km = s[ind : ind + k1]
        db[km] = db.get(km, 0) + 1
    for key, val in db.items():
        print(key, val)


def main(args):
    """ Main entry point of the app """
    letters = "ACGT"
    s = ""
    count = 0
    while True:
        for i in range(60):
            s += letters[random.randint(0, 3)]
        if countkmer(s, 3, 6):
            printkmer(s, 3, 6)
            break
        if count > 1000:
            print("No sequence found!")
            break
        count += 1
    if args.log:
        with open("README.txt", "a") as fout:
            fout.write("[{}]\t[{}]\n".format(time.asctime(), " ".join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    # parser.add_argument("infile", help="Input file")

    # Optional argument flag which defaults to False
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        default=False,
        help="Save command to 'README.txt'",
    )

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-n", "--name", action="store", dest="name")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, etc)"
    )

    # Specify output of '--version'
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()
    main(args)
