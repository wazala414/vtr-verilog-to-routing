#!/usr/bin/env python3

import sys
import re
import os
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--output_dir", default=".", help="Directory to place arch xml files")
args = parser.parse_args()

openlist = []

side = ['lt','lr','lb','tr','tl','tb','rb','rl','rt','br','bl','bt','bb','tt','rr','ll']
W = 50
filename = "/home/vm/VTR-Tools/workspace/Basic_Architecture/switchbox_out.xml"

f = open(filename, "w")
perm = None
for x in range(len(side)):
    for y in range(int(W/2)):
        perm = y+1
        #print(perm)
        f.write('<func type="')
        f.write("%s" % side[x])
        f.write('" formula="t+')
        f.write("%i" % perm)
        f.write('"/>\n')
