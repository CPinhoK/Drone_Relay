import json
import paho.mqtt.client as mqttclient
from geopy import distance
import time
from classes import Drone
from classes import Station
from classes import Package

def on_connect():
    pass

connected = False
broker_address = "192.168.98.11"
topic = "vanetza/in/cam"
m = "{\"accEngaged\":false,\"acceleration\":10,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":3601,\"headingConf\":127,\"latitude\":400000000,\"length\":100,\"longitude\":-80000000,\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":16383,\"speedConf\":127,\"speedLimiter\":true,\"stationID\":1,\"stationType\":15,\"width\":30,\"yawRate\":0}"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqttclient.Client("MQTT")
    client.on_connect = on_connect
    client.connect(broker_address)
    return client


def publish(client):
    msg_count = 0
    msg = f"messages: {msg_count}"
    result = client.publish(topic, m)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{m}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    msg_count += 1


def read_sim_info(file):
    f = open(file)
    data = json.load(f)
    return data


def run():
    client = connect_mqtt()
    client.loop_start()

    sim_info = read_sim_info('simulation.json')
    
    time_interval = 0.1

    drones_list = []
    stations_list = []
    package_origin = (sim_info['origin']['latitude'], sim_info['origin']['longitude'])
    package_destination = (sim_info['destination']['latitude'], sim_info['destination']['longitude'])
    package = Package(sim_info['package'])

    for i in range(len(sim_info['drones'])):
        drones_list.append(Drone(i, sim_info['drones'][i]))

    for j in range(len(sim_info['stations'])):
        new_station = Station(j, sim_info['stations'][j])
        new_station.parked_drones = [d for d in drones_list if d.id in new_station.parked_drones]
        stations_list.append(new_station)


    while True:
        #publish(client)

        # The package didn't arrive to destination yet
        if distance.distance(package.position, package_destination).m > 100:
            print("Package didn't arrive to destination yet")
            
            # The package is moving, the drone should go in direction of destination
            if package.carried_by != None:
                current_drone = package.carried_by
                print("Package is moving")

                # Check if drone han enough battery to reach package_destination
                if distance.distance(current_drone.position, package_destination) < current_drone.get_available_range():
                    pass
                current_drone.move_forward(package_destination, time_interval)
                package.position = current_drone.position
            
            # The package is not moving, it should be picked up by a drone
            else:
                print("Package is NOT moving")
                closest_station = stations_list[0]
                for station in stations_list:
                    if distance.distance(package.position, station.position) < distance.distance(package.position, closest_station.position):
                        closest_station = station
                
                closest_station.get_available_drone().pick_package(package)

        time.sleep(time_interval)
                


if __name__ == '__main__':
    run()