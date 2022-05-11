#!/usr/bin/env python3

#-----------------------------------------------------------------------------------------------
# Author:       Victor Marot - University of Bristol
# Date:         11/05/2022
#
# Description:  This script aims at creating a fully connected custom switchblock pattern, 
#               with or without same side (u-turn), while a FULL preset is being developed
#               to directly implement it within VTR.
#               In the architecture, <switchfuncs> should be written and closed on a different 
#               line, the script will then populate it.
#               
#
# Args: --in_arch   -> The location and name of the inputted architecture
#       --out_arch  -> (If specified) The output architecture destination and name
#       --size      -> The amount of tracks on one side
#       --same_side -> Adds same side connections (u-turn) to the connection list
#-----------------------------------------------------------------------------------------------

import os
from queue import Empty
import string
import traceback
import sys
import re
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--in_arch", default="/home/vm/VTR-Toolsworkspace/architectures/Arch_Test_Same_Side.xml", help="Directory to get arch xml files from.")
parser.add_argument("--out_arch", nargs='?', const="/home/vm/VTR-Tools/workspace/architectures/Arch_Test_Same_Side_Test.xml", help="Directory to write arch xml files to.")
parser.add_argument("--size", default="100", help="Amount of tracks in a channel.")
parser.add_argument("--same_side", action="store_true", help="Describes if same side connections (u-turn) are required.")
args = parser.parse_args()

openlist = []
data = []
line_index = 0
comment = False
# TODO: Use routing width to set number
W = int(args.size)

# Set of sides to connect to
side_bidir = ['lt','lr','lb','tr','tb','rb']
side_unidir = ['lt','lr','lb','tr','tl','tb','rb','rl','rt','br','bl','bt']
if args.same_side:
    side_bidir.extend(['bb','tt','rr','ll'])
    side_unidir.extend(['bb','tt','rr','ll'])

# Overwrite architecture file if no output has been specified
if args.out_arch:
    out_arch_name = args.out_arch
else:
    out_arch_name = args.in_arch    

# Regex declaration
re_width = re.compile('.*<fixed_layout.*width=\"(?:(?P<width>\d+))\"')
re_height = re.compile('.*<fixed_layout.*height=\"(?:(?P<height>\d+))\"')
re_directionality = re.compile('.*type="(?:(?P<directionality>unidir|bidir))\"')
re_func_start = re.compile('.*<switchfuncs>')
re_func = re.compile('.*<func\s.*\/\>')
re_start_com = re.compile('.*<!--')
re_end_com = re.compile('.*-->')

with open(args.in_arch, "r") as in_arch:
    print('Input architecture loaded from: %s\n' % args.in_arch)
    for line in in_arch:
        # Checks whether the match has been found as a comment to avoid writing commented permutations
        if re.match(re_start_com, line):
            comment = True
        if (re.match(re_end_com, line)):
            comment = False

        # Remove permutation expression from line
        if re.match(re_func, line) and not comment:        
            line = line.replace(re.match(re_func, line).group(),"")
            if not line.isspace():
                # Add data line to the buffer list if line has not been rendered empty
                data.append(line)
        
        # Add data line to the buffer list
        else:
            data.append(line)
        
        # Finds directionality of the architecture (assuming it is the same for the entire architecture)
        match_directionality = re.match(re_directionality,line)
        if match_directionality:
            direction = match_directionality.group('directionality')

with open(out_arch_name, "w") as out_arch:
    print('Output architecture written to: %s\n' % out_arch_name)
    for line in data:
        match_func_start = re.match(re_func_start, line)
        
        # Checks whether the match has been found as a comment to avoid writing commented permutations
        if re.match(re_start_com, line):
            comment = True
        if (re.match(re_end_com, line)):
            comment = False
        if not comment:

            # When match is found, start iterating to write permutations
            if match_func_start:
                if direction == 'bidir':
                    for x in range(len(side_bidir)):
                        for y in range(int(W/2)):
                            perm = y
                            data.insert(line_index+1, '<func type="%s'  % side_bidir[x] + '" formula="t+%i' % perm + '"/>\n')
                else:
                    for x in range(len(side_unidir)):
                        for y in range(int(W/2)):
                            perm = y
                            data.insert(line_index+1, '<func type="%s'  % side_unidir[x] + '" formula="t+%i' % perm + '"/>\n')
            
        line_index += 1
    out_arch.writelines(data)