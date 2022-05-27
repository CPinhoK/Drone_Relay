class Drone():
    def __init__(self, id, drone_info) -> None:
        self.id = id
        self.latitude = drone_info.latitude
        self.longitude = drone_info.longitude
        self.speed = drone_info.speed
        self.acceleration = drone_info.acceleration
        self.battery = 100
        self.hasCargo = False
        self.moving = False
        self.neighborsInRange = []
        
    def move_forward(self, latitude, longitude):
        pass

    def move_to_station(self):
        pass

    def drop_package(self):
        pass

    def pick_package(self):
        pass

    def send_cam(self):
        pass

    def send_denm(self):
        pass


class Station():
    def __init__(self, station_info) -> None:
        self.id = station_info.id
        self.latitude = station_info.latitude
        self.longitude = station_info.longitude
        self.drones = []

    def receive_denm(self, drone_id):
        pass

