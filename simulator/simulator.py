import json
import paho.mqtt.client as mqttclient
from geopy import distance
import time
from classes import Drone
from classes import Station
from classes import Package

connected = False
broker_address = "192.168.98.11"

stations_addresses = ["192.168.98.11", "192.168.98.12", "192.168.98.13", "192.168.98.14", "192.168.98.15"]
drones_addresses = ["192.168.98.21", "192.168.98.22", "192.168.98.23", "192.168.98.24", "192.168.98.25", "192.168.98.26", "192.168.98.27", "192.168.98.28", "192.168.98.29", "192.168.98.30"]

drones_list = []
stations_list = []
package = None

topic_cam_in = "vanetza/in/cam"
topic_cam_out = "vanetza/out/cam"
topic_denm_in = "vanetza/in/denm"
topic_denm_out = "vanetza/out/denm"
m = "{\"accEngaged\":false,\"acceleration\":10,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":3601,\"headingConf\":127,\"latitude\":400000000,\"length\":100,\"longitude\":-80000000,\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":16383,\"speedConf\":127,\"speedLimiter\":true,\"stationID\":1,\"stationType\":15,\"width\":30,\"yawRate\":0}"

def connect_mqtt(addr):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker! " + str(client._client_id.decode()))
            client.subscribe(topic_denm_out)
        else:
            print("Failed to connect, return code %d\n", rc)
    
    def on_message(client, userdata, msg): # The callback for when a PUBLISH message is received from the server.
        print("<<Message received>> by " + client._client_id.decode()[-2:] + " " + msg.topic + " " + str(msg.payload))  # Print a received msg
        msg_dict = json.loads(msg.payload)['fields']['denm']
        if msg_dict['situation']['eventType']['causeCode'] == 45 and client._client_id.decode()[-2:] == str(msg_dict['situation']['eventType']['subCauseCode']):
            drone = None
            for d in drones_list:
                if d.client._client_id.decode()[-2:] == str(msg_dict['situation']['eventType']['subCauseCode']):
                    drone = d
                    break
            drone.pick_package(package)
        else:
            pass

    client = mqttclient.Client(addr)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(addr)
    return client


def publish(client, topic, msg):
    msg = msg.replace("\'", "\"")
    msg_count = 0
    #msg = f"messages: {msg_count}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}` of `{client._client_id.decode()[-2:]}`")
    else:
        print(f"Failed to send message to topic {topic}")
    msg_count += 1


def read_info(file):
    f = open(file)
    data = json.load(f)
    return data


def run():
    sim_info = read_info('simulation.json')
    time_interval = 0.1

    cam_template = read_info('in_cam.json')
    denm_template = read_info('in_denm.json')

    package_origin = (sim_info['origin']['latitude'], sim_info['origin']['longitude'])
    package_destination = (sim_info['destination']['latitude'], sim_info['destination']['longitude'])
    global package
    package = Package(sim_info['package'])
    #print("PACKAGE " + str(package))

    for i in range(len(sim_info['drones'])):
        new_drone = Drone(i, sim_info['drones'][i])
        new_drone.client = connect_mqtt(drones_addresses[i])
        new_drone.client.loop_start() # Connect to brocker
        drones_list.append(new_drone)
        

    for j in range(len(sim_info['stations'])):
        new_station = Station(j, sim_info['stations'][j])
        new_station.parked_drones = [d for d in drones_list if d.id in new_station.parked_drones]
        new_station.client = connect_mqtt(stations_addresses[j])
        new_station.client.loop_start() # Connect to brocker
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
                
                next_drone = closest_station.get_available_drone()

                msg = denm_template
                msg['situation']['eventType']['causeCode'] = 45
                msg['situation']['eventType']['subCauseCode'] = int(next_drone.client._client_id.decode()[-2:])
                
                publish(closest_station.client, topic_denm_in, str(msg))

        time.sleep(time_interval)
                


def block_unreachable_devices():
    pass


if __name__ == '__main__':
    run()