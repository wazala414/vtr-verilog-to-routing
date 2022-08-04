from utils import *

###################################
# Node class, representing each switch and terminal

class Node:
    def __init__(self,id,isTerminal):
        self.id = id
        self.N_edge = None
        self.E_edge = None
        self.S_edge = None
        self.W_edge = None
        self.N_node = None
        self.E_node = None
        self.S_node = None
        self.W_node = None
        self.isTerminal = isTerminal
        self.config = []
        self.routedNodes = [(None,None)]

    def __str__(self):
        return str(self.id)

    def getX(self):
        return int(self.id[0])    

    def getY(self):
        return int(self.id[1])

    def printConfig(self):
        if len(self.config) == 0:
            return "Unconnected"
        else:
            return str(self.config)

    def checkTurn(self,dest,routeid):
        try:
            dir = self.getDir(dest.getID())
        except:
            return False
        edge = self.getEdge(dir)
        # if no current net exists on the edge, valid turn
        if edge.netName == None:
            return True
        # otherwise, valid turn if nets are the same
        if matchingRouteID(edge.netName,routeid):
            return True
        else:
            return False

    ###############################        
    # Set configuration of node according to a route from src to dest through self
    # Check if valid by checking if edge already in use by a different net
    def route(self,src_node,dest_node,routeid):
        # Determine which outgoing edge is required
        if self.N_node != None:
            if compareID(self.N_node.getID(),dest_node):
                edge = self.N_edge
        if self.E_node != None:
            if compareID(self.E_node.getID(),dest_node):
                edge = self.E_edge
        if self.S_node != None:
            if compareID(self.S_node.getID(),dest_node):
                edge = self.S_edge
        if self.W_node != None:
            if compareID(self.W_node.getID(),dest_node):
                edge = self.W_edge
        
        if edge.netName == None:
            edge.netName = routeid
        elif not matchingRouteID(edge.netName,routeid):
            raise Exception(f"Route conflict when trying to route {routeid} - edge already used by {edge.netName}")
        
        src_dir = self.getDir(src_node)
        dest_dir = self.getDir(dest_node)
        self.config.append((src_dir,dest_dir))
        
    def getDir(self,id):
        
        if compareID(self.N_node.getID(),id):
            return 'N'
        if compareID(self.E_node.getID(),id):
            return 'E'
        if compareID(self.S_node.getID(),id):
            return 'S'
        if compareID(self.W_node.getID(),id):
            return 'W'
        raise Exception("Not found direction")

    def getID(self):
        return self.id
    
    def getEdge(self,dir):
        if dir=='N':
            return self.N_edge
        elif dir=='E':
            return self.E_edge
        elif dir=='S':
            return self.S_edge
        elif dir=='W':
            return self.W_edge
        else:
            raise Exception("Invalid dirs")

    ####################################
    # addEdge and addNode used in construction of SB
    def addEdge(self,edge,dir):
        if dir=='N':
            edge.connectNode(self)
            self.N_edge = edge
        elif dir=='E':
            edge.connectNode(self)
            self.E_edge = edge
        elif dir=='S':
            edge.connectNode(self)
            self.S_edge = edge
        elif dir=='W':
            edge.connectNode(self)
            self.W_edge = edge
        else:
            raise Exception("Invalid dirs")

    def addNode(self,node,dir):
        if dir=='N':
            self.N_node = node
        elif dir=='E':
            self.E_node = node
        elif dir=='S':
            self.S_node = node
        elif dir=='W':
            self.W_node = node
        else:
            raise Exception("Invalid dirs")

    #########################################
    # Return which node is attached to a terminal
    def getNodeFromTerminal(self):
        # If terminal, then get attached node
        if self.N_node != None:
            return self.N_node
        elif self.E_node != None:
            return self.E_node
        elif self.S_node != None:
            return self.S_node
        elif self.W_node != None:
            return self.W_node
        else:
            raise Exception("No node attached to terminal")  

class Edge:
    def __init__(self,id):
        self.node1 = None #Node 1 is the primary node - edge is always South or East of Node 1
        self.node2 = None
        self.netName = None
        self.id = id

    def getID(self):
        return self.id

    def getNetName(self):
        return self.netName

    def connectNode(self,node):
        if self.node1 == None:
            self.node1 = node
        elif self.node2 == None:
            self.node2 = node
        else:
            raise Exception("More than two nodes connected to edge (ID:"+str(self.id)+")!")

    def getOtherNode(self,curr_node):
        if self.node1 == curr_node:
            return self.node2
        elif self.node2 == curr_node:
            return self.node1
        else:
            raise Exception("Invalid node")


######################################
# Swich box class, made from a grid of nodes and edges       
class Switchbox:
    def __init__(self,width,demands):
        self.nodes = []
        self.terminals = []
        self.edges = []
        self.demands = []
        self.used = []
        self.routes = []
        self.routeids = []
        self.width = width

        # Check demands and set
        if demands != None:
            self.setDemands(demands)
        
         # Create nodes and append to self.nodes list
        for i in range(0,self.width):
            new_col = []
            for j in range(0,self.width):
                newNode = Node((i,j),False)
                new_col.append(newNode)
            self.nodes.append(new_col)        
        
        # Connect all nodes together via an edge
        for col in range(0,width):
            for row in range(0,width):
                if col == 0:
                    self.connectTwoNodes(self.nodes[col][row],'E',self.nodes[col+1][row],'W')
                elif col == width-1:
                    self.connectTwoNodes(self.nodes[col-1][row],'E',self.nodes[col][row],'W')
                else:
                    self.connectTwoNodes(self.nodes[col][row],'E',self.nodes[col+1][row],'W')
                    self.connectTwoNodes(self.nodes[col-1][row],'E',self.nodes[col][row],'W')

                if row == 0:
                    self.connectTwoNodes(self.nodes[col][row],'S',self.nodes[col][row+1],'N')
                elif row == width-1:
                    self.connectTwoNodes(self.nodes[col][row-1],'S',self.nodes[col][row],'N')
                else:
                    self.connectTwoNodes(self.nodes[col][row],'S',self.nodes[col][row+1],'N')
                    self.connectTwoNodes(self.nodes[col][row-1],'S',self.nodes[col][row],'N')



        # Create terminals - give them an ID tuple and connect them to the appropriate node via an edge
        for x in range(0,self.width):
            id = ('N',x)
            t = Node(id,True)
            self.connectTwoNodes(t,'S',self.nodes[x][0],'N')
            self.terminals.append(t)

            id = ('E',x)
            t = Node(id,True)
            self.connectTwoNodes(t,'W',self.nodes[width-1][x],'E')
            self.terminals.append(t)

            id = ('S',x)
            t = Node(id,True)
            self.connectTwoNodes(t,'N',self.nodes[x][width-1],'S')
            self.terminals.append(t)

            id = ('W',x)
            t = Node(id,True)
            self.connectTwoNodes(t,'E',self.nodes[0][x],'W')
            self.terminals.append(t)
  
    def copy(self):
        sb_new = Switchbox(self.width,None)
        sb_new.width = self.width
        sb_new.nodes = self.nodes.copy()
        sb_new.terminals = self.terminals.copy()
        sb_new.edges = self.edges.copy()
        sb_new.demands = self.demands.copy()
        sb_new.routes = self.routes.copy()
        sb_new.routeids = self.routeids.copy()

        return sb_new

    def connectTwoNodes(self,node1,node1_dir,node2,node2_dir):
        
        # Add each other on their list of nodes
        node1.addNode(node2,node1_dir)
        node2.addNode(node1,node2_dir)

        # Now create and add the edges

        # Form edge ID
        if (node1_dir == 'E') or (node1_dir == 'S'):
            edgeid = str(node1.getID()) + "-" + node1_dir
        elif (node2_dir == 'E') or (node2_dir == 'S'):
            edgeid = str(node2.getID()) + "-" + node2_dir


        if node1.getEdge(node1_dir) == None:
            if node2.getEdge(node2_dir) == None:
                # No edge exists so create one
                edge = Edge(edgeid)
                self.edges.append(edge)
                node1.addEdge(edge,node1_dir)
                node2.addEdge(edge,node2_dir)
            else:
                edge = node2.getEdge(node2_dir)
                node1.addEdge(edge,node1_dir)
        else:
            if node2.getEdge(node2_dir) == None:
                # No edge exists so create one
                edge = node1.getEdge(node1_dir)
                node2.addEdge(edge,node2_dir)

    ############################################    
    # Double check demands are valid
    def setDemands(self,demands):
        for demand in demands:
            for node in demand:
                (side,val) = node
                assert (side=='N') or (side=='W') or (side=='S') or (side=='E'), "Invalid demand for node " + str(node) 
                assert (val>-1) and (val<self.width), "Invalid demand for node " + str(node)       
        self.demands = demands

    def printDemands(self):
        print("Demands:")
        for demand in self.demands:
            print(str(demand[0]) + " <--> " + str(demand[1]))

    def printConnections(self):
        for col in range(0,self.width):
            for row in range(0,self.width):
                node = self.nodes[col][row]
                print("Node: " + str(node) + "  ",end='')
                print("Connected to " + str(node.N_node) + str(node.E_node) + str(node.S_node) + str(node.W_node),end='')
                print(" - Config: " + node.printConfig())
            print("")

    def printEdges(self):
        dirs = ['N','E','S','W']
        for col in self.nodes:
            for n in col:
                print("Node: " + str(n.getID()) + " -> ",end='')
                for dir in dirs:
                    if n.getEdge(dir) != None:
                        print(str(n.getEdge(dir).getID()) + " ",end='')
        print("Terminals: ")
        for t in self.terminals:
            print("Node: " + str(t.getID()) + " -> ",end='')
            for dir in dirs:
                if t.getEdge(dir) != None:
                    print(str(t.getEdge(dir).getID()) + " ",end='')

    def getNodesOfEdge(self,edgeid):
        for e in self.edges:
            if e.getID() == edgeid:
                print("For edge" + str(e.getID()) + " -> Node1: = " + str(e.node1.getID()) + " Node2: " + str(e.node2.getID()))

    def getNode(self,nodeid):
        for t in self.terminals:
            if t.getID() == nodeid:
                return t
        for col in self.nodes:
            for n in col:
                if (n.getID()) == nodeid:
                    return n
    def addRoutes(self,routes):
        for route in routes:
            self.addRoute(route)
            
    def addRoute(self,route):
        # Takes a route between two terminals, works out node config, adds this to the Sb and removes used edges
        
        self.routes.append(route)
        routeid = (route[0],route[-1])
        self.routeids.append(routeid)
        src = route[0]
        dest = route[-1]

        assert (src[0] == 'N') or (src[0] == 'E') or (src[0] == 'S') or (src[0] == 'W'), "Route does not start at a terminal"
        assert (dest[0] == 'N') or (dest[0] == 'E') or (dest[0] == 'S') or (dest[0] == 'W'), "Route does not finish at a terminal"
        for i in range(0,len(route)-2):
            curr = self.getNode(route[i+1])
            try:
                curr.route(route[i],route[i+2],routeid)
            except:
                raise Exception(f"Route conflict when routing {routeid}")

    def checkRoute(self,route):
        routeid = (route[0],route[-1])
        src = route[0]
        dest = route[-1]
        assert (src[0] == 'N') or (src[0] == 'E') or (src[0] == 'S') or (src[0] == 'W'), "Route does not start at a terminal"
        assert (dest[0] == 'N') or (dest[0] == 'E') or (dest[0] == 'S') or (dest[0] == 'W'), "Route does not finish at a terminal"
        
        for i in range(0,len(route)-2):
            curr = self.getNode(route[i+1])
            try: 
                curr.route(route[i],route[i+2],routeid)
            except:
                return False
        return True

    ########################################
    # Check if a move from src to dest is valid, by comparing route IDs
    def checkTurn(self,src,dest,routeid):
        src = self.getNode(src)
        dest = self.getNode(dest)
        if src.checkTurn(dest,routeid):
            return True
        else:
            return False

    def resetSB(self):
        for row in self.nodes:
            for n in row:
                n.config = []
        for e in self.edges:
            e.netName = None
        self.used = []
        self.routes = []
        self.routeids = []
        

    def exportConfig(self):
        f = open("sb_config",'w')
        for col in self.nodes:
            for n in col:
                line = str(n.getID()) + "," + str(n.config) + "\n"
                f.write(line)
        f.close()
