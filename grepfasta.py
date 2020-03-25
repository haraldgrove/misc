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
import os.path
import gzip


def getfasta(fastafile, pattern, full=False, reverse=False):
    """
    Sends any sequence with name matching the pattern to stdout
    :param fastafile: Input fastafile, plain text
    :param pattern: Whole or part of sequence name
    :return: NA
    """
    active = False
    if fastafile[-3:] == ".gz":
        op = gzip.open
    else:
        op = open
    with op(fastafile, "rt") as fin:
        for line in fin:
            if line.startswith(">"):
                if (not full and pattern in line) or (full and pattern == line.strip()[1:]):
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
    trans = str.maketrans("ACGTacgt", "TGCAtgca")
    active = False
    if fastafile[-3:] == ".gz":
        op = gzip.open
    else:
        op = open
    seq = ""
    with op(fastafile, "rt") as fin:
        for line in fin:
            if line.startswith(">"):
                if active:
                    if not reverse:
                        sys.stdout.write("{}\n".format(seq[start:end]))
                    else:
                        sys.stdout.write(
                            "{}\n".format(seq[start:end][::-1].translate(trans))
                        )
                    seq = ""
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
                    sys.stdout.write("{}\n".format(seq[start:end]))
                else:
                    sys.stdout.write(
                        "{}\n".format(seq[start:end][::-1].translate(trans))
                    )


def getbedfasta(fastafile, bedfile):
    """
    Sends sequence selection of any sequence with name matching pattern to stdout
    :param fastafile: Input fastafile, plain text
    :param bedfile: Name of bedfile with sequence coordinates
    :return:
    """
    bed = {}
    with open(bedfile, "r") as fin:
        for line in fin:
            l = line.strip().split()
            if len(l) == 6:
                chrom, start, end, name, score, strand = l
            elif len(l) == 4:
                chrom, start, end, name = l
                strand = "+"
            elif len(l) == 3:
                chrom, start, end = l
                name = "{}:{}-{}".format(chrom, start, end)
                strand = "+"
            elif len(l) == 1:
                chrom = l[0]
                start = end = 0
                name = "{}:{}-{}".format(chrom, start, end)
                strand = "+"
            else:
                continue
            if chrom not in bed:
                bed[chrom] = []
            bed[chrom].append((name, int(start), int(end), strand))
    trans = str.maketrans("ACGTacgt", "TGCAtgca")
    active = False
    if fastafile[-3:] == ".gz":
        op = gzip.open
    else:
        op = open
    seq = ""
    with op(fastafile, "rt") as fin:
        for line in fin:
            if line.startswith(">"):
                if active:
                    for (name, start, end, strand) in bed[chrom]:
                        if end == 0:
                            end = len(seq)
                        if strand == "+":
                            sys.stdout.write(">{}\n{}\n".format(name, seq[start:end]))
                        else:
                            sys.stdout.write(
                                ">{}\n{}\n".format(
                                    name, seq[start:end][::-1].translate(trans)
                                )
                            )
                    seq = ""
                chrom = line[1:].strip().split()[0]
                if chrom in bed:
                    active = True
                else:
                    active = False
            elif active:
                seq += line.strip()
        else:
            if active:
                for (name, start, end, strand) in bed[chrom]:
                    if end == 0:
                        end = len(seq)
                    if strand == "+":
                        sys.stdout.write(">{}\n{}\n".format(name, seq[start:end]))
                    else:
                        sys.stdout.write(
                            ">{}\n{}\n".format(
                                name, seq[start:end][::-1].translate(trans)
                            )
                        )


def main(args):
    """ Main entry point of the app """
    if os.path.isfile(args.pattern):
        getbedfasta(args.fastafile, args.pattern)
    else:
        if args.coordinates == "0,0":
            getfasta(args.fastafile, args.pattern, args.full, args.reverse)
        else:
            s, e = [int(c) for c in args.coordinates.split(",")]
            getpartialfasta(args.fastafile, args.pattern, s - 1, e, args.reverse)
    if args.log:
        with open("README.txt", "a") as fout:
            fout.write("[{}]\t[{}]\n".format(time.asctime(), " ".join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("pattern", help="Search pattern or bed-file")
    parser.add_argument("fastafile", help="Input fasta file")

    # Optional argument flag which defaults to False
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        default=False,
        help="Save command to 'README.txt'",
    )

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument(
        "-c",
        "--coordinates",
        help="Base pair coords. (1-based): begin,end",
        default="0,0",
    )
    parser.add_argument(
        "-f", "--full", action="store_true", default=False, help="Full title"
    )
    parser.add_argument(
        "-r", "--reverse", action="store_true", default=False, help="Reverse strand"
    )

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
