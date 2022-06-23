import json
import paho.mqtt.client as mqttclient
from geopy import distance
import time
import os
import requests
from classes import Drone
from classes import Station
from classes import Package

INIT_BLOCK = True

connected = False
broker_address = "192.168.98.11"

stations_addresses = ["192.168.98.11", "192.168.98.12", "192.168.98.13", "192.168.98.14", "192.168.98.15"]
drones_addresses = ["192.168.98.21", "192.168.98.22", "192.168.98.23", "192.168.98.24", "192.168.98.25", "192.168.98.26", "192.168.98.27", "192.168.98.28", "192.168.98.29", "192.168.98.30"]

drones_list = []
stations_list = []
package = None
enter_new_station = False

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

        # if message received by RSU (station) with OBU (drone) battery status
        # only one station will receive this DENM because of range 
        
        elif client._client_id.decode()[-2:] in ['11', '12', '13', '14', '15']:
            print("ID: " + client._client_id.decode()[-2:])
            print("originating ID: " + str(msg_dict['management']['actionID']['originatingStationID']))
            station = [s for s in stations_list if s.client._client_id.decode()[-2:] == client._client_id.decode()[-2:]][0]
            next_d = station.receive_denm(msg_dict)
            if(isinstance(next_d, Drone)):
                package.carried_by = next_d
                package.print_carried_by()
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

    for i in range(len(sim_info['drones'])):
        new_drone = Drone(i, sim_info['drones'][i])
        new_drone.client = connect_mqtt(drones_addresses[i])
        new_drone.client.loop_start() # Connect to brocker
        drones_list.append(new_drone)
        update_map_drone(new_drone.client._client_id.decode()[-2:], new_drone.latitude, new_drone.longitude, new_drone.hasCargo, new_drone.battery)
        

    for j in range(len(sim_info['stations'])):
        new_station = Station(j, sim_info['stations'][j])
        new_station.parked_drones = [d for d in drones_list if d.id in new_station.parked_drones]
        new_station.client = connect_mqtt(stations_addresses[j])
        new_station.client.loop_start() # Connect to brocker
        stations_list.append(new_station)
        update_map_station(new_station.client._client_id.decode()[-2:], new_station.latitude, new_station.longitude, [d.id for d in new_station.parked_drones])


    os.chdir('../../vanetza')
    if INIT_BLOCK:
        block_by_range()

    while True:
        #publish(client)

        # The package didn't arrive to destination yet
        if distance.distance(package.position, package_destination).m > 100:
            print("Package didn't arrive to destination yet")
            
            # The package is moving, the drone should go in direction of destination
            if package.carried_by != None:
                current_drone = package.carried_by
                print("Package is moving")
                
                # Check if drone has enough battery to reach package_destination
                if distance.distance(current_drone.position, package_destination) > current_drone.get_available_range():
                    if current_drone.battery < 40:
                        # battery status
                        sub_cause_code = 3
                        if current_drone.battery <= 33:
                            sub_cause_code = 1
                        elif current_drone.battery <= 66:
                            sub_cause_code = 2
                        current_drone.send_denm(32, sub_cause_code)
                        current_drone.send_denm(34, 55)

                current_drone.move_forward(package_destination, time_interval)
                package.position = current_drone.position

                update_map_drone(current_drone.client._client_id.decode()[-2:], current_drone.position[0], current_drone.position[1], current_drone.hasCargo, current_drone.battery)
                update_in_range(current_drone)
            
            # The package is not moving, it should be picked up by a drone
            else:
                print("Package is NOT moving")
                closest_station = stations_list[0]
                for station in stations_list:
                    if distance.distance(package.position, station.position) < distance.distance(package.position, closest_station.position):
                        closest_station = station
                
                next_drone = closest_station.get_available_drone()

                # Build and send DENM message with the id of drone that should pick the package
                msg = denm_template
                msg['management']['stationType'] = 15
                msg['situation']['eventType']['causeCode'] = 45
                msg['situation']['eventType']['subCauseCode'] = int(next_drone.client._client_id.decode()[-2:])
                publish(closest_station.client, topic_denm_in, str(msg))

        time.sleep(time_interval)


def update_in_range(drone):
    drone_id = drone.client._client_id.decode()[-2:]
    closest_station = None

    for s in stations_list:
        s_id = s.client._client_id.decode()[-2:]
        if s_id != drone_id:
            if distance.distance(drone.position, s.position).m < 500 and s != drone.last_station:
                os.system(f'docker-compose exec obu-{drone_id} unblock 6e:06:e0:03:00:{s_id}')
                os.system(f'docker-compose exec rsu-{s_id} unblock 6e:06:e0:03:00:{drone_id}')

                os.system(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{drone.last_station.client._client_id.decode()[-2:]}')
                os.system(f'docker-compose exec rsu-{drone.last_station.client._client_id.decode()[-2:]} block 6e:06:e0:03:00:{drone_id}')

                drone.last_station = s
                closest_station = s
                enter_new_station = True
                break

    if closest_station != None:
        for d in drone.last_station.parked_drones:
            d_id = d.client._client_id.decode()[-2:]
            if d_id != drone_id:
                if distance.distance(drone.position, d.position).m > 500:
                    #print(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{d_id} block 6e:06:e0:03:00:{drone_id}')
                else:
                    os.system(f'docker-compose exec obu-{drone_id} unblock 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{d_id} unblock 6e:06:e0:03:00:{drone_id}')
    else:
        for d in drone.last_station.parked_drones:
            d_id = d.client._client_id.decode()[-2:]
            if d_id != drone_id:
                if distance.distance(drone.position, d.position).m > 500:
                    #print(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{d_id} block 6e:06:e0:03:00:{drone_id}')
                else:
                    os.system(f'docker-compose exec obu-{drone_id} unblock 6e:06:e0:03:00:{d_id}')
                    os.system(f'docker-compose exec obu-{d_id} unblock 6e:06:e0:03:00:{drone_id}')    


""" def block_by_range():
    for drone in drones_list:
        drone_id = drone.client._client_id.decode()[-2:]
        for d in [x for x in drones_list if x != drone]:
            d_id = d.client._client_id.decode()[-2:]
            if distance.distance(drone.position, d.position).m > 500:
                #print(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                os.system(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
        
        for s in stations_list:
            s_id = s.client._client_id.decode()[-2:]
            if distance.distance(drone.position, s.position).m > 500:
                os.system(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{s_id}')
                os.system(f'docker-compose exec rsu-{s_id} block 6e:06:e0:03:00:{drone_id}')
            else:
                drone.last_station = s

    for station in stations_list:
        station_id = station.client._client_id.decode()[-2:]
        for s in [x for x in stations_list if x != station]:
            s_id = s.client._client_id.decode()[-2:]
            if distance.distance(station.position, s.position).m > 500:
                #print(f'docker-compose exec obu-{drone_id} block 6e:06:e0:03:00:{d_id}')
                os.system(f'docker-compose exec rsu-{station_id} block 6e:06:e0:03:00:{s_id}') """

def block_by_range():
    for drone in drones_list:      
        for s in stations_list:
            s_id = s.client._client_id.decode()[-2:]
            if distance.distance(drone.position, s.position).m < 500:
                drone.last_station = s
                
        
def update_map_station(id, lat, long, parked_drones):
    data={"id": str(id),"lat": float(lat),"lon": float(long),"drones": parked_drones}
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    payload = dict(data)
    url = "http://127.0.0.1:8000/station"
    res = requests.post(url,headers=headers,json=payload)

def update_map_drone(id, lat, long, has_cargo, battery):
    data={"id": str(id),"lat": float(lat),"lon": float(long),"has_package": has_cargo, "battery": battery}
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    payload = dict(data)
    url = "http://127.0.0.1:8000/drone"
    res = requests.post(url,headers=headers,json=payload)

if __name__ == '__main__':
    run()