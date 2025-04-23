import time, sys, math, machine

# STTS22H settings

devaddr = 0x3C     # default address

shutdowndelay = 1 # delay in milliseconds between power down mode and 1 Hz rate

powerdown = 0x00    # power down mode

set1hz = 0x04   # 1Hz mode

autoincr = 0x04 # enable autoincrement

ctrlreg = 0x04 # control register

statreg = 0x05 # status register

busyflg = 0x01 # busy flag - status register

temp_0_3 = 0x06 # temperature value (low nibble) register
temp_4_7 = 0x07 # temperature value (high nibble) register

# NOTE - BOOT button is to the left of the Qwicc connector (USB conn. facing top, Qwicc conn. facing bottom)


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
    ----------------------------
    ------ INITIALIZATION ------
    ----------------------------
"""

# --- Set up I2C communication ---

bus = machine.I2C(0, scl=machine.Pin(13), sda=machine.Pin(12))      

# --- Set Mode ---

# 1. set Power Down mode
val = i2c.readfrom_mem(devaddr,ctrlreg,1)      # read control register
val &= 0xFE     # reset one-shot indicator
bus.write_byte_data(devaddr, ctrlreg, val)      # refresh control register

# 2. Wait to reach power down mode
time.sleep_ms(shutdowndelay)

# 3. Set 1Hz mode ---
val = i2c.readfrom_mem(devaddr,ctrlreg,1)       # read control register
val |= 0x80     # set 1Hz mode bit
bus.write_byte_data(devaddr, ctrlreg, val)      # refresh control register

# 4. Set enable autoincrement ---
val = i2c.readfrom_mem(devaddr,ctrlreg,1)       # read control register
val |= 0x08     # set enable-autoincrement bit
bus.write_byte_data(devaddr, ctrlreg, val)      # refresh control register

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
for i in range(1,cycls):

    # --- Wait until temperature data extraction completed
    busyval = 0x01
    while busyval == 0x01:      
        val = bus.read_byte_data(devaddr, statreg)       # read status register
        busyval = val & busystat
        
    # --- Retrieve extracted temperature data
    tempr = bus.read_i2c_block_data(devaddr, temp_0_3, 2)
    val = (tempr[1]<<8)|tempr[0]

    # --- Temperature raw data conversionn to Centigrade & Fahrenheit
    tempc = float(val)/100.0 if val < 32768 else float(val-65536)/100.0
    tempf = 1.8*tempc + 32
    
    cycldata.append(tempc)
    
    time.sleep(cyclwait)
    print("Did reading "+str(i))
    
intvals = DoSpectrum(cycldata, dminintval, splttr)

# Display the buckets

for i in range(len(intvals)):
    print(str(i)+": ["+str(intvals[i][1][0])+", "+str(intvals[i][1][1])+"] - "+str(intvals[i][0]))

