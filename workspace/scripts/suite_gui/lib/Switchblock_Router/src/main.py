from stats import getFullReport
from switchbox import Switchbox
from gui import *
from utils import *
from routing import *
from testing import routeTestSingle, routeTestBatch

# demands = parseDemands("demands.txt")

# sb = Switchbox(10,demands)
# sb.printDemands()

# Hadlocks(sb)
# print(getFullReport(sb))
# drawSB(sb)       

sb = routeTestSingle(12,"Hadlocks",False,False,10)
print(getFullReport(sb))
drawSB(sb)
