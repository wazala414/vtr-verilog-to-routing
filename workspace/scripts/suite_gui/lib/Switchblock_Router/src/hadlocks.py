#Q-negative - further away from dest (return only unvisited)
def getQNegativeNeighbours(node, dest, width, visited,sb,routeid):
    neighbours_temp = []
    neighbours = []
    x_node = node[0]
    y_node = node[1]
    x_dest = dest[0]
    y_dest = dest[1]

    if x_dest > x_node:
        if x_node-1 >= 0:
            neighbours_temp.append((x_node-1,y_node))
    elif x_node > x_dest:
        if x_node+1 <= width-1:
            neighbours_temp.append((x_node+1,y_node))
    else:
        if x_node-1 >= 0:
            neighbours_temp.append((x_node-1,y_node))
        if x_node+1 <= width-1:
            neighbours_temp.append((x_node+1,y_node))

    if y_dest > y_node:
        if y_node-1 >= 0:
            neighbours_temp.append((x_node,y_node-1))
    elif y_node > y_dest:
        if y_node+1 <= width-1:
            neighbours_temp.append((x_node,y_node+1))
    else:
        if y_node-1 >= 0:
            neighbours_temp.append((x_node,y_node-1))
        if y_node+1 <= width-1:
            neighbours_temp.append((x_node,y_node+1))

    for n in neighbours_temp:
        if n not in visited:
            
            if sb.checkTurn(node,n,routeid) == True:
                neighbours.append(n)

    return neighbours

#Q-positive - closer to dest (return only unvisited)
def getQPositiveNeighbours(node, dest, width, visited,sb,routeid):
    neighbours = []
    neighbours_temp = []
    x_node = node[0]
    y_node = node[1]
    x_dest = dest[0]
    y_dest = dest[1]

    if x_dest > x_node:
        neighbours_temp.append((x_node+1,y_node))
    elif x_node > x_dest:
        neighbours_temp.append((x_node-1,y_node))

    if y_dest > y_node:
        neighbours_temp.append((x_node,y_node+1))
    elif y_node > y_dest:
        neighbours_temp.append((x_node,y_node-1))

    for n in neighbours_temp:
        if n not in visited:
            
            if sb.checkTurn(node,n,routeid) == True:
                neighbours.append(n)

    return neighbours

def stack(target_stack, input):
    if input == None:
        return 0
    if type(input) is list:
        for x in input:
            target_stack.append(x)
    else:
        target_stack.append(input)

def unstack(target_stack):
    return target_stack.pop(-1)

def removeVisitedFromStack(node,p_stack,n_stack):
    if node in p_stack:
        p_stack.remove(node)
    if node in n_stack:
        n_stack.remove(node)

def varyByOne(node1,node2):
    diffx = node1[0] - node2[0]
    diffy = node1[1] - node2[1]
    if (diffx==1 or diffx==-1) and diffy==0:
        return True
    if (diffy==1 or diffy==-1) and diffx==0:
        return True
    return False

def refineRoute(route,sb,routeid):
    # Route will have wrong turns in it - sort this out by working backwards through route, and finding the valid one
    new_route = []
    curr_node = route[-1]
    new_route.append(curr_node)
    for i in range(len(route)-2,-1,-1):
        if sb.checkTurn(curr_node,route[i],routeid):
            curr_node = route[i]
            new_route.append(curr_node)
    new_route.reverse()
    return new_route


def HadlocksAlgo(width,demand,sb,routeid):
    #demand = ((0,0),(7,4))
    visited = []
    # print(demand)
    p_stack = []
    n_stack = []
    route = []

    src = demand[0]
    dest = demand[1]
    d = 0
    u_node = src
    route.append(u_node)
    while u_node != dest:
        visited.append(u_node)
        removeVisitedFromStack(u_node,p_stack,n_stack)
        stack(n_stack,getQNegativeNeighbours(u_node,dest,width,visited,sb,routeid))
        # If no unlabeled Q-Positive neighbours...
        if not getQPositiveNeighbours(u_node,dest,width,visited,sb,routeid):
            
            # If nothing in p_stack
            # print("Step 3")
            if not p_stack:
                if not n_stack:
                    raise Exception("No path exists")
                # P stack empty, then copy n-stack into p-stack
                else:
                    # print("Step 4")
                    p_stack = n_stack.copy()
                    d = d+1
            # print("Step 3, part 2")
            u_node = unstack(p_stack)        
            
        
        else:
        # Set u_node to be an unlabeled Q-positive, and stack any additional q-positives
            qpos_neighbours = getQPositiveNeighbours(u_node,dest,width,visited,sb,routeid)
            u_node = qpos_neighbours.pop(0)
            stack(p_stack,qpos_neighbours)
           
        route.append(u_node)
        
    final = refineRoute(route,sb,routeid)

    return final



