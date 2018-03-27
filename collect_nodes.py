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

def read_nodes(args):
    data = {}
    tree = {}
    most = 0
    c1, c2 = args.columns.split(',')
    with open(args.infile, 'r') as fin:
        for line in fin:
            if line.startswith('#'):
                continue
            l = line.strip().split()
            try:
                name1, name2 = l[int(c1)-1], l[int(c2)-1]
            except IndexError:
                continue
            key = tuple(sorted([name1,name2]))
            if key not in data:
                data[key] = []
            data[key].append(l)
            if name1 not in tree:
                tree[name1] = []
            if name2 not in tree:
                tree[name2] = []
            if name2 not in tree[name1]:
                tree[name1].append(name2)
                most = max(len(tree[name1]),most)
            if name1 not in tree[name2]:
                tree[name2].append(name1)
                most = max(len(tree[name2]), most)
    print('Most connections: {}'.format(most))
    return tree, data

def go_wide(tree, node1, data, fout):
    if node1 not in tree:
        return
    nodes = tree.pop(node1)
    for node2 in nodes:
        key = tuple(sorted([node1, node2]))
        if key not in data:
            continue
        lines = data.pop(key)
        for line in lines:
            fout.write('{}\n'.format('\t'.join(line)))
        go_wide(tree, node2, data, fout)

def collect_nodes(args, tree, data):
    with open(args.output, 'w') as fout:
        while len(tree) > 0:
            first = random.choice(list(tree.keys()))
            fout.write('#------------------------\n')
            go_wide(tree, first, data, fout)

def filter_nodes(args):
    if args.filter:
        fullname =  args.infile
    else:
        fullname = args.output
    prefix = fullname.rsplit('.', 1)[0]
    fileA = '{}.A.txt'.format(prefix)
    fileB = '{}.B.txt'.format(prefix)
    c1, c2 = [int(c)-1 for c in args.columns.split(',')]
    with open(fullname, 'r') as fin, open(fileA, 'w') as foutA, open(fileB, 'w') as foutB:
        lines, countA, countB = [], [], []
        sizesA, sizesB = [], []
        for line in fin:
            if line.startswith('#'):
                if len(countA) > 1:
                    foutA.write('#{};{}------------------------\n'.format(len(countA), sum(sizesA)))
                if len(countB) > 1:
                    foutB.write('#{};{}------------------------\n'.format(len(countB), sum(sizesB)))
                for items in lines:
                    if len(countA) > 1:
                        foutA.write(items)
                    if len(countB) > 1:
                        foutB.write(items)
                lines, countA, countB = [], [], []
                sizesA, sizesB = [], []
                continue
            l = line.strip().split()
            lines.append(line)
            if l[c1] not in countA:
                countA.append(l[c1])
                sizesA.append(int(l[c1+2]))
            if l[c2] not in countB:
                countB.append(l[c2])
                sizesB.append(int(l[c2 + 2]))

def main(args):
    """ Main entry point of the app """
    if not args.filter:
        print('Reading nodes')
        tree, data = read_nodes(args)
        print('Collecting groups')
        collect_nodes(args, tree, data)
    filter_nodes(args)

    if args.log:
        with open('README.txt', 'a') as fout:
            fout.write('[{}]\t[{}]\n'.format(time.asctime(), ' '.join(sys.argv)))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("infile", help="Input file")

    # Optional argument flag which defaults to False
    parser.add_argument('-l', '--log', action="store_true", default=False, help="Save command to 'README.txt'")
    parser.add_argument('-f', '--filter', action="store_true", default=False, help="Only run filter step")

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-c", "--columns", help="Columns with nodes", default="1,2")

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
