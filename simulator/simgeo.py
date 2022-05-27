import time
from geopy import distance as dt
base_a=(40.634143433650856, -8.631619736734109 )
pickup_loc=(40.637188008105035, -8.632518395421563 )
target_loc=(40.68212993837249, -8.513696932084093  )


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

lis = gen_cords(base_a,pickup_loc,5)
print(lis)
for i in range(len(lis)-1):
    d=dt.distance(lis[i],lis[i+1])
    print(i)
    print(d.meters)