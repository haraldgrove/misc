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
from operator import itemgetter
import numpy as np

def regions(args):
    """
    Condenses a read-depth file by calculating the average read depth pr. region
    :param args:
    :return:
    """
    beddb = {}
    with open(args.bedfile, 'r') as fin:
        for line in fin:
            name, start, stop, *rest = line.strip().split()
            if name not in beddb:
                beddb[name] = []
            beddb[name].append([int(start), int(stop)])
    samples = []
    rname, rstart, rstop = '', 0, 0
    outfile = '{}.regions.txt'.format(args.infile[0].rsplit('.',1)[0])
    with open(args.infile[0], 'r') as fin, open(outfile, 'w') as fout:
        entry = 0
        for line in fin:
            name, pos, *depth = line.strip().split()
            if name not in beddb:
                continue
            pos = int(pos)
            if len(samples) == 0:
                samples = [0]*len(depth)
            if rname == '' or rname != name or pos > rstop:
                if rname != '':
                    fout.write('{}\t{}\t{}\t{}\n'.format(rname, rstart, rstop,
                                                         '\t'.join([str(s/entry) for s in samples])))
                    samples = [0] * len(depth)
                for ind, el in enumerate(beddb[name]):
                    if pos >= el[0] and pos <= el[1]:
                        rstart, rstop = beddb[name].pop(ind)
                        rname = name
                        entry = 0
                        break
                    else:
                        rname, rstart, rstop = '', 0, 0
                        entry = 0
                if rname == '':
                    continue
            for i, e in enumerate(depth):
                samples[i] += int(e)
            entry += 1
        if rname != '':
            fout.write('{}\t{}\t{}\t{}\n'.format(rname, rstart, rstop, '\t'.join([str(s/entry) for s in samples])))

def reference(args):
    db = {}
    outfile = '{}.{}.dist.txt'.format(args.infile[0].rsplit('.', 1)[0], args.chrom)
    with open(args.infile[0], 'r') as fin, open(outfile, 'w') as fout:
        entry = 0
        for line in fin:
            name, start, stop, *depth = line.strip().split()
            db[(name,start,stop)] = [float(d) for d in depth]
        for key1, val1 in db.items():
            dist = []
            if key1[0] != args.chrom:
                continue
            for key2, val2 in db.items():
                if key1 == key2:
                    continue
                #d = sum([(a - b)**2 for a,b in zip(val1, val2)])
                d = np.corrcoef(val1,val2)[0,1]
                if np.isnan(d):
                    d = 0
                dist.append(key2+(abs(d),))
            val = sorted(dist, key=itemgetter(3), reverse=True)
            k = '{}:{}-{}'.format(key1[0], key1[1], key1[2])
            a = '\t'.join(['{}:{}-{};{:.6f}'.format(b[0],b[1],b[2],b[3]) for b in val[0:100]])
            fout.write('{}\t{}\n'.format(k,a))

def compare(args):
    db = {}
    with open(args.infile[1], 'r') as fin:
        for line in fin:
            el = line.strip().split()
            db[el[0]] = [e.split(';')[0] for e in el[1:]]
    outfile = 'compare.txt'
    with open(args.infile[0], 'r') as fin, open(outfile, 'w') as fout:
        for line in fin:
            el = line.strip().split()
            key = el[0]
            val = [e.split(';')[0] for e in el[1:]]
            if key not in db:
                fout.write('{}\tmissing\n'.format(key))
                continue
            old = db[key]
            x = set(val)
            y = set(old)
            same = len(x.intersection(y))
            fout.write('{}\t{}\n'.format(key,same))


def main(args):
    """ Main entry point of the app """
    if args.option=='regions':
        regions(args)
    elif args.option=='reference':
        reference(args)
    elif args.option=='compare':
        compare(args)
    if args.log:
        with open('README.txt', 'a') as fout:
            fout.write('[{}]\t[{}]\n'.format(time.asctime(), ' '.join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("option", help="Operation")
    parser.add_argument("infile", nargs='*', help="Input file")

    # Optional argument flag which defaults to False
    parser.add_argument('-l', '--log', action="store_true", default=False, help="Save command to 'README.txt'")

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-b", "--bedfile", help='Bedfile')
    parser.add_argument("-c", "--chrom", help='Limit analysis to this chromosome')
    parser.add_argument("-n", "--name", action="store", dest="name")

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
