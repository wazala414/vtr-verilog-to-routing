#!/usr/bin/python3
import argparse
from multiprocessing.sharedctypes import Value
import subprocess
import csv
import os
import sys

def getDemands(line):
    demands = []
    # print(line)
    for d in line:

        demand = list(d.split(" "))
        
        if len(demand)==2:
            demands.append(demand[0] + ',' + demand[1] + ' ')
        elif len(demand)>2:
            # Remove duplicates
            demand = list(set(demand))
            for i in range(0,len(demand)):
                for j in range(i,len(demand)):
                    if i==j:
                        continue
                    demands.append(demand[i] + ',' + demand[j] + ' ')
    # print(demands)
    return demands



    
def sb_route(
    width,
    alpha,
    iterations,
    target,
    demand_file,
    output_file,
    algorithm,
    objective
    ):
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    cmd = [os.path.join(curr_dir,'./routing')]

    cmd += [
        '-w', str(width),
        '-a', str(alpha),
        '-n', str(iterations),
        '-t', str(target),
        '-o', str(output_file),
        '-r', str(algorithm),
        '-j', str(objective)
    ]
    
    with open(os.path.join(curr_dir,demand_file),newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            # Relative Path -> Better to use absolute path
            #sb_name = output_file
            #sb_name = os.path.join(curr_dir,sb_name)
            #f = open(sb_name,"w")
            #f.close()
            #curr_cmd = cmd + ['-o',sb_name]

            for line in reader:
                line.pop(0)
                xcord = line.pop(0)
                ycord = line.pop(0)
                id = str(xcord + ',' + ycord)
                curr_cmd = cmd + ['-i',id]

                # sb_name = f"sb_x{xcord}_y{ycord}_routing.csv"
                # sb_name = "sb_out.txt"
                # sb_name = os.path.join(curr_dir,sb_name)
                # curr_cmd = cmd + ['-o',sb_name]


                demands = (getDemands(line))           
                
                if demands:
                    print(f"\nRouting SB_x{xcord}_y{ycord}...\n")
                    subprocess.run(curr_cmd+demands)

def cpp_compiling():
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.isfile(os.path.join(curr_dir,'./routing')):
        make_progress = subprocess.Popen("make", shell=True, stdout=subprocess.PIPE, stderr=sys.stdout.fileno())
        make_progress.wait()


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='Routes signals inside a switchblock matrix')
    ap.add_argument('-width', required=True, help='Channel width of the FPGA architecure (ie. track #)')
    ap.add_argument('-alpha', required=False, default='0.95', help='Alpha parameter of the router')
    ap.add_argument('-iter', required=False, default='500', help='Maximum number of iteration of the router')
    ap.add_argument('-target', required=False, default='0.9', help='Algorithm will return when all paths routed AND total length < (optimal length / target)')
    ap.add_argument('-demand', required=False, default='SB_database_sample.csv', help='File path for the CSV file to be used for the routing demands')
    ap.add_argument('-out', required=False, default='sb_out.csv', help='File path for output CSV file logging the routing paths')
    ap.add_argument('-alg', required=False, default='1', help='ID of the routing algorithm: 1=Random Hadlocks, 2=Hadlocks, 3=Simulated Annealing')
    ap.add_argument('-print', required=False, default='False', action='store_true', help='Print result on console')
    ap.add_argument('-obj', required=False, default='1', help='Objective function (1-MINSUM, 2-MINMAX)')
    args = ap.parse_args()

    #########################################
    WIDTH=args.width                        # Switch box width
    ALPHA=args.alpha                        # Alpha parameter (default 0.95)    
    ITERATIONS=args.iter                    # Max number of iterations of annealing algoritm
    TARGET=args.target                      # Algorithm will return when all paths routed AND total length < (optimal length / target)
    DEMAND_FILE=args.demand                 # File path for demands csv
    OUTPUT=args.out                         # Provide location and name of output file
    ALGORITHM=args.alg                      # Choose algorithm
    OBJECTIVE=args.obj                      # Objective function
    #########################################

    # Check if c++ binary exists, otherwise compile it
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.isfile(os.path.join(curr_dir,'./routing')):
        make_progress = subprocess.Popen("make", shell=True, stdout=subprocess.PIPE, stderr=sys.stdout.fileno())
        make_progress.wait()

    sb_route(width=WIDTH,alpha=ALPHA,iterations=ITERATIONS,target=TARGET,demand_file=DEMAND_FILE,output_file=OUTPUT,algorithm=ALGORITHM,objective=OBJECTIVE)  