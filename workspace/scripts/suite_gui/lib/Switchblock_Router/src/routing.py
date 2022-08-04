from math import factorial
import random
import hadlocks
import sys
import itertools
import copy
import simulated_annealing
from stats import getMaxRouteLength, getTotalManhatten, getTotalRouteLength
from utils import startprogress, progress, endprogress, show_progressbar

# def RandomWalk(sb):
#     route_iterations = 0
#     all_routes = []
#     route_done = False
    
#     for demand in sb.demands:        
#         route = []
#         curr_node = [0,0]
#         new_node = [0,0]
#         src = sb.getNode(demand[0])
#         dest = sb.getNode(demand[1])
#         first_node = src.getNodeFromTerminal().getID()
#         last_node = dest.getNodeFromTerminal().getID()
#         curr_node[0] = int(first_node[0])
#         curr_node[1] = int(last_node[1])
#         routeid = (src.getID(),dest.getID())
#         route.append(demand[0])
#         route.append(src)
#         success = True
#         while tuple(curr_node) != last_node:
#             new_node = curr_node
#             if (curr_node[0] == last_node[0]):
#                 if last_node[1]>curr_node[1]:
#                     new_node[1] = curr_node[1] + 1
#                 else:
#                     new_node[1] = curr_node[1] - 1
#             elif (curr_node[1] == last_node[1]):
#                 if last_node[0]>curr_node[0]:
#                     new_node[0] = curr_node[0] + 1
#                 else:
#                     new_node[0] = curr_node[0] - 1
#             else:       
#                 choice = random.randint(0,1)
#                 if choice==1:
#                     if last_node[0]>curr_node[0]:
#                         new_node[0] = curr_node[0] + 1
#                     else:
#                         new_node[0] = curr_node[0] - 1
#                 else:
#                     if last_node[1]>curr_node[1]:
#                         new_node[1] = curr_node[1] + 1
#                     else:
#                         new_node[1] = curr_node[1] - 1
                        
#             if sb.checkTurn(tuple(curr_node),tuple(new_node),routeid):
#                     curr_node = new_node
#                     route.append(tuple(curr_node))
#                     print(curr_node)
#             else:
#                 success = False
#                 break
#                 raise Exception("Routing failed")

#         if success==True: 
#             route.append(demand[-1])
#             sb.addRoute(route)
#             all_routes.append(route)
    
#     return len(all_routes)
        
        
        
                       
#############################################
# Implement hadlock algorithm on each demand in turn
# Return number of successfully routed demands

def SimAnnealing(sb):
    return simulated_annealing.SimAnnealingAlgo(sb)

def Hadlocks(sb):
    used_nodes = []
    routed_success = 0
    
    if show_progressbar == True:
        print("Routing demands using Hadlocks Algorithm...")
        startprogress("Routing")
    
    for demand in sb.demands:
        # print("Routing -> ",end='')
        # print(demand)
        src = sb.getNode(demand[0])
        dest = sb.getNode(demand[1])
        routeid = (src.getID(),dest.getID())
        firstNode = src.getNodeFromTerminal()
        lastNode = dest.getNodeFromTerminal()
        try:
            route = hadlocks.HadlocksAlgo(sb.width,(firstNode.getID(),lastNode.getID()),sb,routeid)
        except:
            continue
        routed_success += 1
        used_nodes = used_nodes + route 
        route.insert(0,src.getID())
        route.append(dest.getID())
        # print(route)
        sb.addRoute(route)   
        if show_progressbar == True: 
            completeness = 100 * sb.demands.index(demand) / len(sb.demands)
            progress(completeness)
    if show_progressbar == True:
        endprogress()
    return routed_success



def RandomHadlocks(sb):
    demands = sb.demands
    target=0.1
    success_counter = 0
    best_route = [] # Remember the best performing solution so far
    
    i = 1
    E = getTotalRouteLength(sb)
    while success_counter != len(demands) or E>=getTotalManhatten(sb)/target:
        success_counter = 0
        
        if i>= 500:
            sb.resetSB()
            if not best_route:
                return 0
            sb.addRoutes(best_route)
            break
        sb.resetSB()
        random.shuffle(sb.demands)
        success_counter = Hadlocks(sb)
        if success_counter>len(best_route):
            best_route = sb.routes.copy()

        E = getTotalRouteLength(sb)
        i += 1
        if show_progressbar:    
            print(f"Failed after {i} attempt(s)")
      
    return success_counter
        
        
def HorizontalFirst(sb):
    route = []
    success_counter = 0
    for demand in sb.demands:
        route = []
        success = True
        curr_node = [0,0]
        src = sb.getNode(demand[0])
        dest = sb.getNode(demand[1])
        routeid = (src.getID(),dest.getID())
        firstNode = src.getNodeFromTerminal()
        lastNode = dest.getNodeFromTerminal()
        last_x, last_y = int(lastNode.getID()[0]), int(lastNode.getID()[1])
        curr_node[0] = int(firstNode.getID()[0])
        curr_node[1] = int(firstNode.getID()[1])
        route.append(src.getID())
        route.append(tuple(curr_node))
        while tuple(curr_node) != lastNode.getID():
            #print("Current node = " + str(curr_node))

            # Unless x values are the same, move horizontally first
            if curr_node[0] != last_x:
                if curr_node[0] < last_x:
                    target = (curr_node[0]+1,curr_node[1])
                else:
                    target = (curr_node[0]-1,curr_node[1])
                #print("Target = " + str(target))
                if sb.checkTurn(tuple(curr_node),tuple(target),routeid):
                    route.append((target))
                    curr_node = target
                    continue
                
            # If x values are the same, or moving horizontally fails, move vertically instead
            if curr_node[1] < last_y:
                target = (curr_node[0],curr_node[1]+1)
            elif curr_node[1] > last_y:
                target = (curr_node[0],curr_node[1]-1)
            else:
                success = False
                break
                raise Exception("Routing failed")
                
            #print("Target = " + str(target))
            # If this works, add to route, otherwise return failed
            if sb.checkTurn(tuple(curr_node),tuple(target),routeid):
                    curr_node = target
                    route.append(tuple(target))
            else:
                success = False
                break
                raise Exception("Routing failed")
        if success==True:
            route.append(dest.getID())
        #print(route)
            sb.addRoute(route)
            success_counter += 1
        
    return success_counter

def RandomHorizontalFirst(sb):
    demands = sb.demands
    target=0.8
    success_counter = 0
    best_route = [] # Remember the best performing solution so far
    i = 1
    E = getTotalRouteLength(sb)
    while success_counter != len(demands) or E>=getTotalManhatten(sb)/target:
        success_counter = 0
        if i>= 500:
            break

        sb.resetSB()
        random.shuffle(sb.demands)
        success_counter = HorizontalFirst(sb)
        if success_counter>len(best_route):
            best_route = sb.routes.copy()
        E = getTotalRouteLength(sb)
        i += 1
    sb.resetSB()
    
    if not best_route:
        return 0
    else:
        sb.addRoutes(best_route)
   

    return success_counter
        
        