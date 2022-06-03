import geo_lib
from geopy import distance

class Drone():
    def __init__(self, id, drone_info):
        self.id = id
        self.latitude = drone_info['latitude']
        self.longitude = drone_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.speed = drone_info['speed']
        self.acceleration = drone_info['acceleration']
        self.battery = 100
        self.max_range = 6
        self.current_race = 0
        self.hasCargo = False
        self.moving = False
        self.neighborsInRange = []
        
    def start_race(self):
        self.current_race = 0
        self.speed = 20
    
    # destination tuple(latitude, longitude); time_interval in seconds
    def move_forward(self, destination, time_interval):
        dist = time_interval*3600/self.speed
        self.position = geo_lib.get_coordinates(self.position, destination, dist)
        self.current_race += dist
        self.update_battery_level()
        print("Drone new position " + str(self.position))

    def move_to_station(self):
        pass

    def drop_package(self):
        pass

    def pick_package(self, package):
        print("Picking package")

        package.carried_by = self
        self.hasCargo = True
        self.start_race()

    def update_battery_level(self, dist):
        self.battery -= dist*100/self.max_range

    def get_available_range(self):
        return self.battery*self.max_range/100

    def send_cam(self):
        pass

    def send_denm(self):
        pass


class Station():
    def __init__(self, id, station_info):
        self.id = id
        self.latitude = station_info['latitude']
        self.longitude = station_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.parked_drones = station_info['parked_drones']
    
    def get_available_drone(self):
        print("Get available drone based on battery level")

        # Choose drone based on battery level
        next_drone = self.parked_drones[0]
        for drone in self.parked_drones:
            if drone.battery > next_drone.battery:
                next_drone = drone

        return next_drone

    def receive_denm(self, drone_id):
        pass
        

class Package():
    def __init__(self, package_info):
        self.latitude = package_info['latitude']
        self.longitude = package_info['longitude']
        self.position = (self.latitude, self.longitude)
        self.carried_by = None

    