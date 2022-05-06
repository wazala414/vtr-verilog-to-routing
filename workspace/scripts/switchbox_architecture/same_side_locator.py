#!/usr/bin/env python3

import os
from queue import Empty
import traceback
import sys
import re
import argparse
import pandas as pd
import xml.etree.ElementTree as et
from xml.etree.ElementTree import tostring


# Arguments
ap = argparse.ArgumentParser(description='Parse information on internal connection of Switchbox')
ap.add_argument('-panda', default=False, action='store_true', required=False, help='Create panda of edges and nodes')
ap.add_argument('-load', default=False, action='store_true', required=False, help='Load previous panda csv')
ap.add_argument('-route_file', required=False, default='/home/vm/VTR-Tools/workspace/Test_Folder/rr_graph2.xml', help='Location of input file containing routing info')
ap.add_argument('-out_file', required=False, default='/home/vm/VTR-Tools/workspace/Test_Folder/Reference/blink/Reference_Arch', help='Location of output file containing match info')
ap.add_argument('-help', required=False, help='List necessary arguments')
args = ap.parse_args()

# Initialization
regex_list = list()
x = 0
y = 0
route = None
line_number = 1

print("Route file in use: " + str(args.route_file) + "\nOutput file in use: " +  str(args.out_file))

out_file = open(args.out_file + '/out_file.txt',"w")

if not args.panda:
    # Regex data structure
    with open(args.route_file, "r") as route_file:

        # Sets values of Regex to use
        re_same_side_1 = re.compile('.+(?:(?P<chan>CHAN[XY]))\s+\((?:(?P<x1>\d+)),(?:(?P<y1>\d+))\)\s+to\s+\((?:(?P<x2>\d+)),(?:(?P<y2>\d+))\)')
        re_same_side_2 = re.compile('.+(?:(?P<chan>CHAN[XY]))\s+\((?:(?P<x1>\d+)),(?:(?P<y1>\d+))\)\s+\)')
        re_same_side_3 = re.compile('.+direction="(INC|DEC)_DIR.+id=\"(?:(?P<id>\d+))\".+type=\"(?:(?P<chan>CHAN[XY]))\".+ptc=\"(?:(?P<ptc>\d+))\".+xhigh\=\"(?:(?P<xh>\d+)).+xlow\=\"(?:(?P<xl>\d+)).+yhigh\=\"(?:(?P<yh>\d+)).+ylow\=\"(?:(?P<yl>\d+))')


        # Loops through line of the route file
        for line in route_file:
            # Finds regex matches
            match_same_side_1 = re.match(re_same_side_1, line)
            match_same_side_2 = re.match(re_same_side_2, line)
            match_same_side_3 = re.match(re_same_side_3, line)
            if match_same_side_1:
                x1 = int(match_same_side_1.group('x1'))
                y1 = int(match_same_side_1.group('y1'))
                x2 = int(match_same_side_1.group('x2'))
                y2 = int(match_same_side_1.group('y2'))
                #print(x1,x2,y1,y2)
                if x1 == x2 and y1 == y2:
                    print("Match found with double coordinates")
            
            if match_same_side_2:
                chan = match_same_side_2.group('chan')
                #print(chan)
                if chan:
                    print("Match found with single coordinates")
            
            if match_same_side_3:
                xh = int(match_same_side_3.group('xh'))
                xl = int(match_same_side_3.group('xl'))
                yh = int(match_same_side_3.group('yh'))
                yl = int(match_same_side_3.group('yl'))
                id = int(match_same_side_3.group('id'))
                chan = match_same_side_3.group('chan')
                ptc = int(match_same_side_3.group('ptc'))
                #print(x1,x2,y1,y2)
                if xh == xl and yh == yl:                
                    out_file.write("Match found with double coordinates at line: " + str(line_number) + "\nid:" + str(id) + " type:" + chan + " ptc:" + str(ptc) + " xh:" + str(xh) + " xl:" + str(xl) + " yh:" + str(yh) + " yl:" + str(yl) + "\n\n")
            line_number += 1

else:
    df_node = pd.DataFrame(columns=['id', 'chan', 'dir', 'ptc', 'xhigh', 'xlow', 'yhigh', 'ylow'])
    df_edge = pd.DataFrame(columns=['sink_node_id', 'src_node_id', 'switch'])

    if not args.load:
        with open(args.route_file, "r") as route_file:

                # Sets values of Regex to use
                re_edges = re.compile('.*<edge\s+sink_node=\"(?:(?P<sink>\d+))\"\s+src_node=\"(?:(?P<src>\d+))\"\s+switch_id=\"(?:(?P<switch>\d+))\"')
                re_nodes = re.compile('.*<loc\s+ptc=\"(?:(?P<ptc>\d+))\".+xhigh=\"(?:(?P<xhigh>\d+))\"\s+xlow=\"(?:(?P<xlow>\d+))\"\s+yhigh=\"(?:(?P<yhigh>\d+))\"\s+ylow=\"(?:(?P<ylow>\d+))\"')
                re_nodes_id = re.compile('.*<node.+id=\"(?:(?P<id>\d+))\".+type=\"(?:(?P<type>.+))\"\>')
                re_nodes_type = re.compile('.*<node.+direction=\"(?:(?P<dir>.+))\".+id=\"(?:(?P<id>.+))\"\s+type=\"(?:(?P<chan>.+))\"\>')

                # Variable for remembering the node ID
                node_id = None
                #node_chan = None
                node_extended = False

                # Loops through line of the route file
                for line in route_file:
                    # Finds regex matches
                    match_edges = re.match(re_edges, line)
                    match_nodes = re.match(re_nodes, line)
                    match_nodes_id = re.match(re_nodes_id, line)
                    match_nodes_type = re.match(re_nodes_type, line)

                    if match_edges:
                        ser_edge = pd.Series(data={'sink_node_id': match_edges.group('sink'), 'src_node_id': match_edges.group('src'), 'switch': match_edges.group('switch')}, index=['sink_node_id', 'src_node_id', 'switch'])
                        df_edge = df_edge.append(ser_edge, ignore_index=True)

                    if match_nodes_type:
                        node_id = match_nodes_type.group('id')
                        node_dir = match_nodes_type.group('dir')
                        node_chan = match_nodes_type.group('chan')
                        node_extended = True

                    elif match_nodes_id:
                        node_id = match_nodes_id.group('id')
                        node_chan = match_nodes_id.group('type')

                    if match_nodes:
                        if node_extended:
                            ser_nodes = pd.Series(data={'id': node_id, 'chan': node_chan, 'dir': node_dir, 'ptc': match_nodes.group('ptc'), 'xhigh': match_nodes.group('xhigh'), 'xlow': match_nodes.group('xlow'), 'yhigh': match_nodes.group('yhigh'), 'ylow': match_nodes.group('ylow')}, index=['id', 'chan', 'dir', 'ptc', 'xhigh', 'xlow', 'yhigh', 'ylow'])
                        else:
                            ser_nodes = pd.Series(data={'id': node_id, 'chan': node_chan, 'dir': '', 'ptc': match_nodes.group('ptc'), 'xhigh': match_nodes.group('xhigh'), 'xlow': match_nodes.group('xlow'), 'yhigh': match_nodes.group('yhigh'), 'ylow': match_nodes.group('ylow')}, index=['id', 'chan', 'dir', 'ptc', 'xhigh', 'xlow', 'yhigh', 'ylow'])
                        df_node = df_node.append(ser_nodes, ignore_index=True)
                        node_extended = False
        
        df_node.to_csv('results/rr_graph_nodes_panda.csv')
        df_edge.to_csv('results/rr_graph_edges_panda.csv')
        print('Processing Finished\nFile Saved')
    else:
        df_node = pd.read_csv('results/rr_graph_nodes_panda.csv')
        df_edge = pd.read_csv('results/rr_graph_edges_panda.csv')
        print('Loading Completed')

    # Correlate location and directions of nodes and the id of nodes constituting the edges and check whether same side happens or not
    # Create output text file for found results
    if os.path.exists('results/output.txt'):
        result = open("results/output.txt", 'w')
    else:    
        result = open("results/output.txt", 'x')

    df_results = pd.DataFrame(columns=['in_id','out_id','in_type','out_type'])

    # Iterates through nodes edges and pickup nodes ids
    for _,iter_node in df_edge.iterrows():
        # Loop through the src node ids that have an edge with the current sink_nodes
        node_in = df_node.loc[df_node['id'] == iter_node[2]]
        node_out = df_node.loc[df_node['id'] == iter_node[1]]
        # if node_in['chan'].values and node_out['chan'].values:
        #     print("Same Channel")
        #     result.write("\nSame Channel")
        # else:
        #     print('Channel In: ', node_in['chan'].values, '\tChannel Out: ', node_out['chan'].values)
        #     result.write('\nChannel In: %s' % node_in['chan'].values + '\tChannel Out: %s' + node_out['chan'].values)
        # if node_in['dir'].values and node_out['dir'].values:
        #     print("Same Direction")
        #     #result.write("\nSame Direction")
        # else:
        #     print('Direction In: ', node_in['dir'].values, '\tDirection Out: ', node_out['dir'].values)
        #     result.write('\nDirection In: %s' % node_in['dir'].values + '\tDirection Out: %s' % node_out['dir'].values)
        # # Syntax to refer to node

        ser_results = pd.Series(data={'in_id': int(node_in['id'].values),'out_id': int(node_out['id'].values),'in_type': node_in['chan'].values,'out_type': node_out['chan'].values}, index=['in_id','out_id','in_type','out_type'])
        df_results = df_results.append(ser_results, ignore_index=True)

        # Output found same side connection
        if (node_in['chan'].values == node_out['chan'].values) and (node_in['dir'].values != node_out['dir'].values) and (node_in['dir'].values and node_out['dir'].values):
            result.write('Found\n')
    
    df_results.to_csv('results/rr_graph_results_panda.csv')
    



