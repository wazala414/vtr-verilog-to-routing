#!/usr/bin/env python3

import sys
import re
import os
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--in_arch", default=".", help="Directory to take arch xml files")
parser.add_argument("--out_arch", default=".", help="Directory to place arch xml files")
parser.add_argument("--size", default=".", help="Size of the FPGA in the form of (x,y)")
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


# TODO: Read size if predefined otherwise use argument, read directionality.
#       Choose sides and W according to read data.
#       Similarly to same_side_locator.py, open arch as read, load in list.
#       Open arch as write, do all the processing and append change to list.
#       Push list to file.