import time
from geopy import distance as dt
base_a=(40.634143433650856, -8.631619736734109 )
pickup_loc=(40.636591182915225, -8.644356258680594 )
target_loc=(40.64107609738405, -8.630484570292488)


centre = (40.63370973647428, -8.665803182942222)


d1=dt.distance(base_a, pickup_loc)
d2=dt.distance(pickup_loc, target_loc)
print(base_a,pickup_loc)
print(d1.meters)


def gen_cords(init,fin,steps):
    pos=[]
    pos.append(init)
    for i in range(steps):
        x=fin[0]-init[0]
        x=init[0]+x*(1+i)/(steps+1)
        y=fin[1]-init[1]
        y=init[1]+y*(1+i)/(steps+1)
        pos.append((x,y))
    pos.append(fin)
    return pos

lis = gen_cords(pickup_loc,target_loc,70)
print(lis)
for i in range(len(lis)-1):
    d=dt.distance(lis[i],lis[i+1])
    #print(i)
    print(d.meters)