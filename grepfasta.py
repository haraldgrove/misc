#!/usr/bin/python3
"""
Note about coordinates:
Start, stop are on the forward strand, indicate reverse strand by using the option "-r".
Coordinates are 1-inclusive [1..N]
"""

__author__ = "Harald Grove"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import time
import sys
import gzip


def getfasta(fastafile, pattern, reverse=False):
    """
    Sends any sequence with name matching the pattern to stdout
    :param fastafile: Input fastafile, plain text
    :param pattern: Whole or part of sequence name
    :return: NA
    """
    active = False
    if fastafile[-3:] == '.gz':
        op = gzip.open
    else:
        op = open
    with op(fastafile, 'rt') as fin:
        for line in fin:
            if line.startswith('>'):
                if pattern in line:
                    active = True
                    sys.stdout.write(line)
                else:
                    active = False
            elif active:
                sys.stdout.write(line)

def getpartialfasta(fastafile, pattern, start, end, reverse):
    """
    Sends sequence selection of any sequence with name matching pattern to stdout
    :param fastafile: Input fastafile, plain text
    :param pattern: Whole or part of sequence name
    :param start: Start coordinate, 0-based. (inclusive)
    :param end: End coordinate, 0-based. (exclusive)
    :return:
    """
    trans = str.maketrans('ACGTacgt', 'TGCAtgca')
    active = False
    if fastafile[-3:] == '.gz':
        op = gzip.open
    else:
        op = open
    seq = ''
    with op(fastafile, 'rt') as fin:
        for line in fin:
            if line.startswith('>'):
                if active:
                    if not reverse:
                        sys.stdout.write('{}\n'.format(seq[start:end]))
                    else:
                        sys.stdout.write('{}\n'.format(seq[start:end][::-1].translate(trans)))
                    seq = ''
                if pattern in line:
                    active = True
                    sys.stdout.write(line)
                else:
                    active = False
            elif active:
                seq += line.strip()
        else:
            if active:
                if not reverse:
                    sys.stdout.write('{}\n'.format(seq[start:end]))
                else:
                    sys.stdout.write('{}\n'.format(seq[start:end][::-1].translate(trans)))


def main(args):
    """ Main entry point of the app """
    if args.coordinates == "0,0":
        getfasta(args.fastafile, args.pattern, args.reverse)
    else:
        s,e = [int(c) for c in args.coordinates.split(",")]
        getpartialfasta(args.fastafile, args.pattern, s-1, e, args.reverse)
    if args.log:
        with open('README.txt', 'a') as fout:
            fout.write('[{}]\t[{}]\n'.format(time.asctime(), ' '.join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument("fastafile", help="Input fasta file")

    # Optional argument flag which defaults to False
    parser.add_argument('-l', '--log', action="store_true", default=False, help="Save command to 'README.txt'")

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-c", "--coordinates", help="Base pair coords. (1-based): begin,end", default="0,0")
    parser.add_argument("-r", "--reverse", action="store_true", default=False, help="Reverse strand")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of '--version'
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s (version {version})'.format(version=__version__))

    args = parser.parse_args()
    main(args)
