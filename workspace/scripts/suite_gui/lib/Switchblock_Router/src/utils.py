import sys
import ast

global show_progressbar 
show_progressbar = False

def manhat(a,b):
    # Return manhattan distance between two coordinates
    ax, ay = a
    bx, by = b
    if ax > bx:
        diffx = ax - bx
    else:
        diffx = bx - ax
    if ay > by:
        diffy = ay - by
    else:
        diffy = by - ay
    return diffx + diffy

#########################################
# For use in checking if two routes are in the same net
# If EITHER the src or dest of either route are the same,
# they are from the same net (so can share edges)
def matchingRouteID(id1,id2):
    if id1[0] == id2[0] or id1[0] == id2[1]:
        return True
    elif id1[1] == id2[0] or id1[1] == id2[1]:
        return True
    else:
        return False

def compareID(id1,id2):
    if id1[0] == id2[0]:
        if id1[1] == id2[1]:
            return True
    return False

def parseDemands(input_file):
    demands = []
    with open(input_file,"r") as demand_file:
        for line in demand_file:
            if len(line) == 0 or line.isspace():
                continue
            line = line.split(',')
            src = line[0]
            dest = line[1]
            demand = ((src[0],int(src[1])),(dest[0],int(dest[1])))
            demands.append(demand)
    return demands

def parseRoutes(input_file):
    routes = []
    curr_route = []
    src = ''
    dest = ''
    with open(input_file,"r") as f:
        for count,line in enumerate(f):
            if ('to' in line and count != 0):
                curr_route.append(ast.literal_eval(dest))
                routes.append(curr_route)
            if 'to' in line:
                src = line.split(' to ')[0]
                dest = line.split(' to ')[1].split('\n')[0]
                
                curr_route = []
                curr_route.append(ast.literal_eval(src))
            elif count != 0:
                curr_route.append(ast.literal_eval((line.split('\n')[0])))
        curr_route.append(ast.literal_eval(dest))
        routes.append(curr_route)
    return routes


def startprogress(title):
    """Creates a progress bar 40 chars long on the console
    and moves cursor back to beginning with BS character"""
    global progress_x
    sys.stdout.write(title + ": [" + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = 0


def progress(x):
    """Sets progress bar to a certain percentage x.
    Progress is given as whole percentage, i.e. 50% done
    is given by x = 50"""
    global progress_x
    percent = x
    x = int(x * 40 // 100)                      
    sys.stdout.write("#" * x + "-" * (40 - x) + "]" + chr(8) * 41 )
    sys.stdout.flush()
    progress_x = x


def endprogress():
    """End of progress bar;
    Write full bar, then move to next line"""
    sys.stdout.write("#" * 40 + "]\n")
    sys.stdout.flush()