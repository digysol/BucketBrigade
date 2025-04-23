import time, math, random

"""
	DpSpetcrum:		    generate a spectrum for a given set of values

	arguments:			a list of numeric values
	                
	return value:		list containing a spectrum each of whose members is a pair
	                    consisting of a count of data points that fit a particular interval
	                    and the interval represented as a 2-value list consisting of 
	                    the minimum and maximum data value represented in this interval
	
"""

def DoSpectrum(valsin, xminintval, xsplttr):

    vals = [float(z) for z in valsin]
    vmax = max(vals)  # largest value retrieved
    vmin = min(vals)  # smallest value retrieved
    # compute the interval size
    dlta  = math.fabs(vmax-vmin)
    ldlta = dlta
    dlta_lim= xminintval*dlta
    while dlta > dlta_lim:
        ldlta = dlta
        dlta = dlta/xsplttr
    dlta = ldlta    # final interval size
    slotcnt = int(math.ceil(math.fabs(vmax-vmin)/dlta)) if dlta > 0 else 1 # number of intervals
    # create the spectrum slots
    slots = []
    slotrng = []
    smin = vmin
    smax = vmin + dlta
    for j in range(0,slotcnt):
        slots.append(0)     # initialize the count slots
        slotrng.append([smin, smax])    # set the value range check slots
        smin = smax
        smax = smin + dlta
    # classify all values by way of counting values on their appropriate interval
    for x in vals: 
        # identify the slot this value fits in
        mbr = [1 if x >= slotrng[y][0] and x <= slotrng[y][1] else 0 for y in range(slotcnt)]
        # update the slot counts per the slot identification operation 
        slots = [slots[y] + mbr[y] for y in range(slotcnt)]
    # normalize the slots per the minimum
    smin = min(slots)
    slots = [[slots[z]-smin,slotrng[z]] for z in range(slotcnt)] 
    return slots    # return the generated spectrum

"""
    --------------------------------
    ------ RUN READING CYCLES ------
    --------------------------------
"""

fdict = open("SpecConfig","r")
config = {z[0]:z[1] for z in [x.split("=") for x in fdict.read().split("\n")[:-1]]}  # NOTE [:-1] needed to remove trailing null in list
fdict.close()

cycls = int(config["CYCLES"])   # number of reading cycles
cyclwait = float(config["CYCLWAIT"])     # wait time between cycles in seconds
dminintval = float(config["MININTVL"])   # weight to determine minimal interval size (default to 0.025)
splttr = float(config["SPLITTR"])      # interval splitter factor (defaul to 2.0)

print(str(cycls)+","+str(cyclwait)+","+str(dminintval)+","+str(splttr))

cycldata = []

busystat = 0x01     # busy bit in status register
for i in range(0,cycls):
            
#    cycldata.append(round(10*random.random(),2))
    cycldata.append(random.randint(1,cycls))
    
    time.sleep(cyclwait)
    print("Did reading "+str(i+1))
    
intvals = DoSpectrum(cycldata, dminintval, splttr)

# Display the buckets

for i in range(len(intvals)):
    print(str(i)+": ["+str(round(intvals[i][1][0],3))+", "+str(round(intvals[i][1][1],3))+"] ( "+str(round(intvals[i][1][1] - intvals[i][1][0],3))+" ) > "+str(round(intvals[i][0],3)))
