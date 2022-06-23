import geo_lib
from geopy import distance
import json
import os
import requests
import time
class Drone():
    def __init__(self, id, drone_info):
        self.id = id
        self.latitude = drone_info['latitude']
        self.longitude = drone_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.speed = drone_info['speed']
        self.acceleration = drone_info['acceleration']
        self.battery = 100
        self.max_range = 6000
        self.current_race = 0
        self.hasCargo = False
        self.moving = False
        self.neighborsInRange = []
        self.last_station = None
        self.istarted=False

        self.client = None
        
    def start_race(self):
        self.current_race = 0
        self.speed = 12000
    
    # destination tuple(latitude, longitude); time_interval in seconds
    def move_forward(self, destination, time_interval):
        dist = time_interval*self.speed/3600*1000
        self.position = geo_lib.get_coordinates(self.position, destination, dist)
        self.current_race += dist

        print("\nDist: " + str(dist))

        self.update_battery_level(dist)
        print("Drone new position " + str(self.position))

    def drop_package(self):
        pass

    def pick_package(self, package):
        print("Drone " + str(self.client._client_id[-2:]) + " picking package")

        package.carried_by = self
        self.hasCargo = True
        self.start_race()

        # battery status
        sub_cause_code = 3
        if self.battery <= 33:
            sub_cause_code = 1
        elif self.battery <= 66:
            sub_cause_code = 2
        self.send_denm(32, sub_cause_code)

    def update_battery_level(self, dist):
        print('\nBattery reduce: ' + str(dist*100/self.max_range))
        self.battery -= dist*100/self.max_range

    def get_available_range(self):
        return self.battery*self.max_range/100

    def send_cam(self):
        pass

    def send_denm(self, cause_code, sub_cause_code):
        f = open('in_denm.json')
        msg = json.load(f)

        msg['management']['actionID']['originatingStationID'] = int(self.client._client_id.decode()[-2:])
        msg['management']['stationType'] = 5
        msg['situation']['eventType']['causeCode'] = cause_code
        msg['situation']['eventType']['subCauseCode'] = sub_cause_code

        msg = str(msg).replace("\'", "\"")
        result = self.client.publish("vanetza/in/denm", msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send {msg} to topic vanetza/in/denm of {self.client._client_id.decode()[-2:]}")
        else:
            print(f"Failed to send message to topic vanetza/in/denm")


class Station():
    def __init__(self, id, station_info):
        self.id = id
        self.latitude = station_info['latitude']
        self.longitude = station_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.parked_drones = station_info['parked_drones']
        self.flying_drones = []
        self.alldrones =[]


        self.client = None
    def rmspecial(self,drone):
        try:
            self.parked_drones.remove(drone)
        except:
            pass
    
    def get_available_drone(self):
        print("Get available drone based on battery level")
        next_drone=None
        try:
            # Choose drone based on battery level
            next_drone = self.parked_drones[0]
            for drone in self.parked_drones:
                if drone.battery > next_drone.battery:
                    next_drone = drone
        except:
            print("itwasempty")
            pass
        
        
        self.parked_drones.remove(next_drone)
        return next_drone

    def receive_denm(self,indic):
        drone_id=indic['management']['actionID']['originatingStationID']
        cause_code=indic['situation']['eventType']['causeCode']
        sub_cause_code=indic['situation']['eventType']['subCauseCode']

        if cause_code==34:
            n_drone=self.get_available_drone()
            print("avaiable drone has id:",n_drone.id)
            if(n_drone==None):
                return n_drone
            for drone in self.parked_drones:
                if n_drone.id==drone.id:    
                    self.parked_drones.remove(n_drone)
            n_drone.hasCargo=True
            self.flying_drones.append(n_drone)
            for drone in self.alldrones:
                print(drone.id)
                if drone_id==drone.id:
                    try:
                        self.flying_drones.remove(drone)
                    except:
                        pass 
                    drone.hasCargo=False
                    print("dist in 34:",distance.distance(drone.position, self.position).m)
                    while(distance.distance(drone.position, self.position).m > 20):
                        print("i wanna move")
                        drone.speed=200
                        drone.move_forward(self.position,0.1)
                        update_map_drone(drone.id,drone.latitude,drone.longitude,drone.hasCargo,drone.battery)
                        #time.sleep(0.05)
                    drone.speed=0
                    self.parked_drones.append(drone)
                    break
            print("message by:",drone_id," inside 34",[d.id for d in self.flying_drones])
            return n_drone
        if cause_code==32:
            print("\nBattery updated for drone " + str(drone_id) + "; batt: " + str(sub_cause_code) + "\n")
            u_drone=None
            #print("message by:",drone_id," inside 32",[d.id for d in self.parked_drones])
            #print("message by:",drone_id," inside 32",[d.id for d in self.flying_drones])
            for drone in self.parked_drones:
                if drone_id==drone.id:
                    u_drone=drone
                    if sub_cause_code==1:
                        drone.battery=33
                    elif sub_cause_code==2:
                        drone.battery=66
                    elif sub_cause_code==3:
                        drone.battery=100
                    break
            for drone in self.flying_drones:
                if drone_id==drone.id:
                    u_drone=drone
                    if sub_cause_code==1:
                        drone.battery=33
                    elif sub_cause_code==2:
                        drone.battery=66
                    elif sub_cause_code==3:
                        drone.battery=100
                    break
            if u_drone==None:
                print("\nError\n")
                return u_drone
            else:
                print("\nU_Droneid:"+str(u_drone.id))
        
        #print("Battery updated for drone " + str(u_drone.id) + "; batt: " + str(sub_cause_code.bat))
        return cause_code
        

class Package():
    def __init__(self, package_info):
        self.latitude = package_info['latitude']
        self.longitude = package_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.carried_by = None

    def print_carried_by(self):
        print("Package carried by drone " , self.carried_by.id)
        
        


def update_map_drone(id, lat, long, has_cargo, battery):
    data={"id": str(id),"lat": float(lat),"lon": float(long),"has_package": has_cargo, "battery": battery}
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    payload = dict(data)
    url = "http://127.0.0.1:8000/drone"
    res = requests.post(url,headers=headers,json=payload)