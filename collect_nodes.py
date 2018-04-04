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
import pandas as pd

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
    """
    Remove
    :param args:
    :return: None
    """
    if args.filter:
        fullname =  args.infile
    else:
        fullname = args.output
    prefix = fullname.rsplit('.', 1)[0]
    fileA = '{}.A.txt'.format(prefix)
    fileB = '{}.B.txt'.format(prefix)
    c1, c2 = [int(c)-1 for c in args.columns.split(',')]
    with open(fullname, 'r') as fin, open(fileA, 'w') as foutA, open(fileB, 'w') as foutB:
        lines = {}
        dbA, dbB = [], []
        for line in fin:
            # Next block starts
            if line.startswith('#'):
                if len(dbA) > 1:
                    foutA.write('#{};{}------------------------\n'.format(len(dbA), sum(sizesA)))
                if len(dbB) > 1:
                    foutB.write('#{};{}------------------------\n'.format(len(dbB), sum(sizesB)))
                for items in lines:
                    if len(dbA) > 1:
                        foutA.write(items)
                    if len(dbB) > 1:
                        foutB.write(items)
                lines, dbA, dbB = [], [], []
                sizesA, sizesB = [], []
                continue
            l = line.strip().split()
            # Filter out very short hits (less than 500 bp, if this doesn't amount to above 80% coverage.
            # Filter out hits with seq ID < 98%
            a, b = [int(x) for x in l[11].split('/')]
            if (a/b) < 0.98:
                continue
            a,b = [int(x) for x in l[13].split('/')]
            if a < 500 and (a / b) < 0.8:
                continue
            lines.append(line)
            name1, name2 = l[c1], l[c2]
            if name1 not in dbA:
                dbA.append(name1)
                sizesA.append(int(l[c2 + 2]))
            if name2 not in dbB:
                dbB.append(l[c2])
                sizesB.append(int(l[c2 + 2]))
        foutA.write('#------------------------\n')
        foutB.write('#------------------------\n')

def clean_df(df):
    """
    Remove alignments (rows) that are 'unecessary', i.e. not helping to bridge any contigs
    :param df:
    :return:
    """
    df = df.sort_values(['name2', 'zstart2+'])
    df = df.reset_index(drop=True)
    deleted = list(df.index)
    prow = None
    for ind, row in df.iterrows():
        if prow is None:
            prow = row
            continue
        if (row['name2'] == prow['name2']) and (row['name1'] != prow['name1']):
            try:
                deleted.pop(deleted.index(ind))
            except (IndexError, ValueError):
                pass
            try:
                deleted.pop(deleted.index(ind-1))
            except (IndexError, ValueError):
                pass
        prow = row
    df = df.drop(df.index[deleted])
    return df

def build_scf(args, df, coll):
    with open(args.output, 'a') as fout:
        df = df.sort_values(['name2','zstart2+'])
        df = df.reset_index(drop=True)
        if args.verbose > 0:
            print(df)
        for ind, row in df.iterrows():
            # We're working on pairs, so just store the first and move on
            if ind == 0:
                prow = row
                continue
            # The two lines have to be from the same sequence in 2 but different sequence in 1
            if (prow['name2'] != row['name2']) or (prow['name1'] == row['name1']):
                prow = row
                continue
            # The distance from the end of the first section to the beginning of the second section
            gap = row['zstart2+'] - prow['end2+']
            # Determining the orientation of the two sections
            if prow['strand2'] == '-':
                pre1 = [prow['zstart1'], '-']
            else:
                pre1 = [prow['size1'] - prow['end1'], '+']
            if row['strand2'] == '-':
                post1 = [row['size1'] - row['end1'], '-']
            else:
                post1 = [row['zstart1'], '+']
            overlap = gap - (pre1[0] + post1[0])
            fout.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(coll, prow['name1'], pre1[1], overlap, row['name1'], post1[1]))
            prow = row

def build_scaffolds(args):
    c1, c2 = [int(c)-1 for c in args.columns.split(',')]
    with open(args.output, 'w') as fout:
        pass
    coll = 0
    with open(args.infile, 'r') as fin:
        lines = []
        for line in fin:
            if line.startswith('#'):
                if len(lines) > 0:
                    df = pd.DataFrame(lines, columns=['score','name1','strand1','size1','zstart1','end1',
                                                      'name2','strand2','size2','zstart2','end2',
                                                      'identity','idPct','coverage','covPct',
                                                      'zstart2+','end2+'])
                    df = df.astype(dtype={'zstart2':'int64','end2':'int64','size2':'int64',
                                          'zstart1':'int64','end1':'int64', 'size1':'int64'})
                    df = clean_df(df)
                    build_scf(args, df, coll)
                    coll += 1
                lines = []
                continue
            l = line.strip().split()
            if l[7] == '-':
                l.append(int(l[8])-int(l[10]))
                l.append(int(l[8])-int(l[9]))
            else:
                l.append(int(l[9]))
                l.append(int(l[10]))
            lines.append(l)

def main(args):
    """ Main entry point of the app """
    if args.build:
        print('Building scaffolds')
        build_scaffolds(args)
    elif args.filter:
        filter_nodes(args)
    else:
        print('Reading nodes')
        tree, data = read_nodes(args)
        print('Collecting groups')
        collect_nodes(args, tree, data)
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
    parser.add_argument('-b', '--build', action="store_true", default=False, help="Only run build step")

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
