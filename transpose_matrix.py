#!/usr/bin/env python3
import sys

infile = sys.argv[1]
i1, i2 = infile.rsplit(".", 1)
outfile = "{}_T.{}".format(i1, i2)
db = []
with open(infile, "r") as fin:
    for line in fin:
        l = line.strip().split()
        db.append(l[3:])
with open(outfile, "w") as fout:
    for line in zip(*db):
        fout.write("{}\n".format("\t".join(line)))
