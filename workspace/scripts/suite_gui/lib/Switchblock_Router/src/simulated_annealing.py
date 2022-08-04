import routing
from switchbox import Switchbox
from stats import getMaxRouteLength, getTotalManhatten, getTotalRouteLength
import random
from math import exp

# Swaps two random elements of the list
def RandomSwap(l):
    if len(l) <= 1:
        return 1
    r1 = 0
    r2 = 0
    while r1 == r2:
        r1 = random.randint(0,len(l)-1)
        r2 = random.randint(0,len(l)-1)
    temp = l[r1]
    l[r1] = l[r2]
    l[r2] = temp



def SimAnnealingAlgo(sb):

    E = 0  # 'Energy' (length)
    R = 0  #  Number of successfuly routed
    alpha = 0.95
    target = 0.8
    M = 500
    k = 1
    boltzmann = 0
    T = 100
    # Initial sequence and routing
    R = routing.Hadlocks(sb)
    E = getTotalRouteLength(sb)
    sol = sb.routes.copy()

    while k<M:

        if E<=getTotalManhatten(sb)/target and R==len(sb.demands):
            break

        if T<1:
            break


        # print(f"Iteration {k}, T={T}, E={E}, R={R}, exp(-deltaE/T)={boltzmann}")
        sb.resetSB()
        RandomSwap(sb.demands)
        R_new = routing.Hadlocks(sb)
        E_new = getTotalRouteLength(sb)
        #E_new = getMaxRouteLength(sb)

        # Step 13
        if R_new>R:
            sol = sb.routes.copy()
            R = R_new
            E = E_new
            T = T*alpha
            #k += 1
        
        # Step 11
        elif R_new == R:
            if E_new < E: #If new solution is shorter (better)
                # Step 13
                sol = sb.routes.copy()
                R = R_new
                E = E_new
                T = T*alpha
                #k += 1
            # Step 12    
            else:
                deltaE = E_new-E
                boltzmann = exp(-deltaE/T)
                if boltzmann > random.uniform(0,1):
                    sol = sb.routes.copy()
                    R = R_new
                    E = E_new
                    T = T*alpha
                    #k += 1
        k += 1       
    if R==len(sb.demands):
        success =  True
    else:
        success = False
    sb.resetSB()
    sb.addRoutes(sol)
    # print(str(k)+";",end='')
    return success
