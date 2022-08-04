from turtle import end_fill
from graphics import *
from switchbox import Switchbox
nodes = []
edges = []
labels = []
terminal_edges = []
colours = ['red','blue','green','greenyellow','indigo','lightcoral','indianred','maroon','coral','burlywood','olive','seagreen','slategrey','indigo','plum']

def drawSB(sb):
    width = sb.width    
    window = 600    # GUI window dimensions (window * window)
    buffer = 50   # Size of white space around SB in window
    terminal_len = 20
    font_size = 6
    win = GraphWin(f"{width}x{width} Switch Box",window,window)
    win.setBackground('white')   
    

    # Calculate location of each node to fit nicely in window
    for i in range(0,width):
        for j in range(0,width):
            n = Circle(Point(int((window-buffer*2)/(width-1)*i + buffer),int((window-buffer*2)/(width-1)*j + buffer)),3)
            n.draw(win)
            nodes.append(n)
    
    # Draw edges between nodes
    for edge in sb.edges:
        if not edge.node1.isTerminal and not edge.node2.isTerminal:
            i,j = edge.node1.getX(),edge.node1.getY()
            p1 = nodes[i*width + j].getCenter()
            i,j = edge.node2.getX(),edge.node2.getY()
            p2 = nodes[i*width + j].getCenter()
            l = Line(p1,p2)
            l.setFill("whitesmoke")    
            edges.append(l)
            l.draw(win)
            
    # Add terminal edges and text labels
    for col in range(0,width):
        for row in range(0,width):
            if col == 0:
                x,y = nodes[col*width + row].getCenter().getX(), nodes[col*width + row].getCenter().getY()
                l = Line(Point(x,y),Point(x-terminal_len,y))
                l.setFill("whitesmoke") 
                l.draw(win)
                terminal_edges.append(l)
                t = Text(Point(x-1.5*terminal_len,y),"W"+str(row))
                t.setSize(font_size)
                t.draw(win)
                labels.append(t)
            if col == width-1:
                x,y = nodes[col*width + row].getCenter().getX(), nodes[col*width + row].getCenter().getY()
                l = Line(Point(x,y),Point(x+terminal_len,y))
                l.setFill("whitesmoke") 
                terminal_edges.append(l)
                l.draw(win)
                t = Text(Point(x+1.5*terminal_len,y),"E"+str(row))
                t.setSize(font_size)
                t.draw(win)
                labels.append(t)
            if row == 0:
                x,y = nodes[col*width + row].getCenter().getX(), nodes[col*width + row].getCenter().getY()
                l = Line(Point(x,y),Point(x,y-terminal_len))
                l.setFill("whitesmoke") 
                l.draw(win)
                terminal_edges.append(l)
                t = Text(Point(x,y-1.5*terminal_len),"N"+str(col))
                t.setSize(font_size)
                t.draw(win)
                labels.append(t)
            if row == width-1:
                x,y = nodes[col*width + row].getCenter().getX(), nodes[col*width + row].getCenter().getY()
                l = Line(Point(x,y),Point(x,y+terminal_len))
                l.setFill("whitesmoke") 
                l.draw(win)
                terminal_edges.append(l)
                t = Text(Point(x,y+1.5*terminal_len),"S"+str(col))
                t.setSize(font_size)
                t.draw(win)
                labels.append(t)

    # Colour route paths
    for i,edge in enumerate(sb.edges):
        if not edge.node1.isTerminal and not edge.node2.isTerminal:
            if edge.getNetName() != None:
                for j,routeid in enumerate(sb.routeids):
                    if edge.getNetName() == routeid:                       
                        edges[i].setFill(colours[j%len(colours)])
    
    # Colour route labels
    for j,routeid in enumerate(sb.routeids):
        str_routeid1 = routeid[0][0] + str(routeid[0][1])
        str_routeid2 = routeid[1][0] + str(routeid[1][1])
        for t in labels:
            if t.getText() == str_routeid1:
                t.setTextColor(colours[j%len(colours)])
                terminal_edges[labels.index(t)].setFill(colours[j%len(colours)])
            if t.getText() == str_routeid2:
                t.setTextColor(colours[j%len(colours)])
                terminal_edges[labels.index(t)].setFill(colours[j%len(colours)])
    
    win.getMouse()
    win.close()




