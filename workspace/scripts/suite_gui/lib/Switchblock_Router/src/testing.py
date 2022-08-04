
from gui import drawSB
from switchbox import Switchbox
import random
from routing import *
from utils import *
from stats import *

# import matplotlib.pyplot as plt
from stats import *
SEED=20
########################
# Generate a single routing test for a set number of demands
def routeTestSingle(width,routing_method,routeback,common_nets,number_demands,corners):
    # random.seed(SEED)
    demands = []
    demands = genDemands(width,number_demands,routeback,common_nets,corners)
    random.seed()
    
    # for d in range(0,number_demands):
    #     # Generate the appropriate number of demands
        
    #     demands.append(genDemand(width,routeback,common_nets,demands))
    
    # Route using given method
    sb = Switchbox(width,demands)

    if routing_method == 'RandomWalk':
        RandomWalk(sb)

    elif routing_method == 'HorizontalFirst':
        HorizontalFirst(sb)

    elif routing_method == 'Hadlocks':
        Hadlocks(sb)

    elif routing_method == 'RandomHadlocks':
        RandomHadlocks(sb)

    elif routing_method == 'SimulatedAnnealing':
        SimAnnealing(sb)
    
    else:
        
        raise Exception("Invalid Routing Method")    
    # Return switch box for further analysis
    return sb

###########################
# Run a number of tests. Run i number of tests (given by 'iterations'), using a set number of demands, increasing up to 'max_demands'
def routeTestBatch(width,routing_method, routeback, common_nets, max_demands, iterations,corners):
    results = []
    demands = ''
    startprogress("Running batch test")
    number_of_demands = range(1,max_demands+1)
    for number_demands in number_of_demands:
        # Repeat up to the maximum number of demands to route

        success_counter = 0

        for i in range(0,iterations):
            
            # For a given number of demands, iterate a certain number of times
            demands = []
            demands = genDemands(width,number_demands,routeback,common_nets,corners)
            # for d in range(0,number_demands):
            #     # Generate the appropriate number of demands
                
            #     demands.append(genDemand(width,routeback,common_nets,demands))
            
            sb = Switchbox(width,demands)
            if routing_method == 'HorizontalFirst':
                routed_success = HorizontalFirst(sb)
                if routed_success == len(demands):
                    success_counter = success_counter + 1   
            
            if routing_method == 'RandomHorizontalFirst':
                routed_success = RandomHorizontalFirst(sb)
                if routed_success == len(demands):
                    success_counter = success_counter + 1  

            if routing_method == 'Hadlocks':
                routed_success = Hadlocks(sb)
                if routed_success == len(demands):
                    success_counter = success_counter + 1   

            if routing_method == 'RandomHadlocks':
                routed_success = RandomHadlocks(sb)
                if routed_success == len(demands):
                    success_counter = success_counter + 1   
                # else:
                #     #print(getAllStats(sb))
                #     #drawSB(sb)
                #     break

            if routing_method == "SimulatedAnnealing":
                if SimAnnealing(sb) == True:
                    success_counter += 1
            
            completeness = 100*((number_demands*iterations+i+1)/((max_demands+1)*iterations))         
            progress(completeness)
        results.append(success_counter)
    endprogress()
    
    percent_results = []
    for i,r in enumerate(results):
        percentage = round(100 * r/iterations,2)
        percent_results.append(percentage)
        print("For " + str(i+1) + " demands, success -> " + str(r) + "/" + str(iterations) + " (" + str(percentage) + "%)")
    for i,r in enumerate(results):
        print(str(round(100 * r/iterations,2)))
    # plt.plot(number_of_demands,percent_results)
    # plt.xlabel("Number of demands")
    # plt.ylabel("Success rate (%)")
    # plt.title(f"{width}x{width} SB using {routing_method} routing algorithm")
    # plt.xticks(range(1,max(number_of_demands)+1,1))
    # plt.show()
    return sb

##########################################
# Generate a pair of two nodes to pass as a demand to be routed
# routeback -> whether the two nodes can be on the same side
# common_nets -> whether any two nodes in a set (prev demands passed as demands) can be the same
# def genDemand(width,routeback,common_nets,demands):
    
#     done = False
    
#     while done == False:
#         done = True
#         d1 = 0
#         d2 = 0
#         d1 = genDest(width)
#         d2 = genDest(width)
#         if d1 == d2:
#             done = False
#         if routeback == False and (d1[0] == d2[0]):
#             done = False
#         if demands and common_nets==False:
#             for prev_demand in demands:
#                 if (d1[0],d1[1]) in prev_demand:
#                     done = False
#                 elif (d2[0],d2[1]) in prev_demand:
#                     done = False

#     demand = ((d1[0],d1[1]),(d2[0],d2[1]))
#     return(demand)


# #################################
# # Generate a random node
# def genDest(width):
    
#     i=0
#     i = random.randint(0,3)
   
#     if i==0:
#         pole = 'N'
#     if i==1:
#         pole = 'E'
#     if i==2:
#         pole = 'S'
#     if i==3:
#         pole = 'W'
#     # Here the corner nodes (=0 and=W-1) and not included to avoid traps
#     i = random.randint(1,width-2)
    
#     return(pole,i)


def genDemands(width,number_of_demands,routeback,common_nets,corners):
    demands = []
    selection = []
    CORNERS = corners
    # 0,width or 1,width-1 depending on if using corner inputs
    if CORNERS==False:
        for i in range(1,width-1):
            selection.append(('N',i))
            selection.append(('E',i))
            selection.append(('S',i))
            selection.append(('W',i))
    elif CORNERS==True:
        for i in range(0,width):
            selection.append(('N',i))
            selection.append(('E',i))
            selection.append(('S',i))
            selection.append(('W',i))
        
    for iteration in range(0,number_of_demands):
        if len(selection)<=1:
            raise Exception("Failed to create demands")
        done = False
        while done == False:
            done = True
            r1 = -1
            r2 = -1
            while r1==r2:
                r1 = random.randint(0,len(selection)-1)
                r2 = random.randint(0,len(selection)-1)
            #print(f"r1={r1},r2={r2},sel_len={len(selection)}    ")
            # Discard if routeback is false and both nodes are same side
            if routeback==False:
                if selection[r1][0] == selection[r2][0]:
                    done = False
                    continue

            if r1>r2:
                demand = ((selection[r1],selection[r2]))
            else:
                demand = ((selection[r2],selection[r1]))

            if demand in demands:
                done = False
                continue

            if common_nets==False:
                if r1 > r2:
                    selection.pop(r1)
                    selection.pop(r2)
                else:
                    selection.pop(r2)
                    selection.pop(r1)

        demands.append(demand)
    return demands

def ExportGenDemands(width,number_of_demands,routeback,common_nets):
    demands = []
    selection = []
    f = open("demands.txt", "w")
    f.close()
    # 0,width or 1,width-1 depending on if using corner inputs
    for i in range(1,width-1):
        selection.append(('N',i))
        selection.append(('E',i))
        selection.append(('S',i))
        selection.append(('W',i))
        
    for iteration in range(0,number_of_demands):
        if len(selection)<=1:
            raise Exception("Failed to create demands")
        done = False
        while done == False:
            done = True
            r1 = -1
            r2 = -1
            while r1==r2:
                r1 = random.randint(0,len(selection)-1)
                r2 = random.randint(0,len(selection)-1)
            #print(f"r1={r1},r2={r2},sel_len={len(selection)}    ")
            # Discard if routeback is false and both nodes are same side
            if routeback==False:
                if selection[r1][0] == selection[r2][0]:
                    done = False
                    continue

            if r1>r2:
                demand = ((selection[r1],selection[r2]))
            else:
                demand = ((selection[r2],selection[r1]))

            if demand in demands:
                done = False
                continue

            if common_nets==False:
                if r1 > r2:
                    selection.pop(r1)
                    selection.pop(r2)
                else:
                    selection.pop(r2)
                    selection.pop(r1)
        f = open("demands.txt",'a')
        f.write(demand[0][0] + '\t')
        f.write(str(demand[0][1]) + '\t')
        f.write(demand[1][0] + '\t')
        f.write(str(demand[1][1]) + '\n')
    f.close()

