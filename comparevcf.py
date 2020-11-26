#! /usr/bin/env python3

import sys

file1 = sys.argv[1]
file2 = sys.argv[2]

fout = None
if len(sys.argv) == 4:
    out2 = sys.argv[3]
    fout = open(out2, 'w')

db = {}
results = [0,0,0] # unique1, unique2, shared
with open(file1, 'r') as fin:
    for line in fin:
        if line.startswith('#'):
            continue
        try:
            chrom, pos, id_, ref, alt, qual, filter_, info, format_, *samples = line.strip().split()
        except ValueError:
            print(line)
            continue
        if len(ref)+len(alt) != 2:
            continue
        db[chrom, pos, ref, alt] = 1
with open(file2, 'r') as fin:
    for line in fin:
        if line.startswith('#'):
            if fout:
                fout.write(line)
            continue
        chrom, pos, id_, ref, alt, qual, filter_, info, format_, *samples = line.strip().split()
        if len(ref) + len(alt) != 2:
            continue
        if filter_ != 'PASS' and filter_ != '.':
            continue
        if (chrom, pos, ref, alt) in db:
            results[2] += 1
            db.pop((chrom, pos, ref, alt))
            filt = 'shared'
        else:
            results[1] += 1
            filt = 'unique'
        if fout and filter_ == 'PASS':
            fout.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(chrom, pos, filt, ref, alt, qual, filter_, info, format_, samples[0]))
    results[0] = len(db)
print('{}\t{}\t{:7}'.format(file1, file2, results[2]))
#print('Shared :{:7}\nUnique1:{:7}\nUnique2:{:7}\n'.format(results[2],results[0],results[1]))
