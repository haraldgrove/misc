#! /usr/bin/env python3
# Combines all SNPs and 

import sys

files = sys.argv[1:]

db = {}
results = [0,0,0] # unique1, unique2, shared
# Reads all variants
for infile in files:
    with open(infile, 'r') as fin:
        for line in fin:
            if line.startswith('#'):
                continue
            try:
                chrom, pos, id_, ref, alt, qual, filter_, info, format_, *samples = line.strip().split()
            except ValueError:
                print(line)
                continue
            if filter_ != 'PASS' and filter_ != '.':
                continue
            if len(ref)+len(alt) != 2:
                continue
            db[chrom, pos, ref, alt] = ['0']*len(files)
# Record presence/absence of each variant
for index, infile in enumerate(files):
    with open(infile, 'r') as fin:
        first = True
        for line in fin:
            if line.startswith('#'):
                continue
            try:
                chrom, pos, id_, ref, alt, qual, filter_, info, format_, *samples = line.strip().split()
            except ValueError:
                print(line)
                continue
            if filter_ != 'PASS' and filter_ != '.':
                continue
            if len(ref)+len(alt) != 2:
                continue
            db[chrom, pos, ref, alt][index] = '1'

for (chrom, pos, ref, alt) in db:
    s = '\t'.join(db[chrom, pos, ref, alt])
    sys.stdout.write('{}\t{}\t{}\t{}\t{}\n'.format(chrom, pos, ref, alt, s))
