import json
import paho.mqtt.client as mqttclient
import time
from classes import Drone
from classes import Station

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


def read_drones_info(file):
    f = open(file)
    data = json.load(f)
    return data


def run():
    client = connect_mqtt()
    client.loop_start()

    DRONES_NUMBER = 10
    STATIONS_NUMBER = 5
    drones_list = []
    info = read_drones_info('Drones.json')

    for i in range(DRONES_NUMBER):
        drones_list.append(Drone(i, info[i]))

    for i in range(STATIONS_NUMBER):
        drones_list.append(Station(i, info[i]))

    while True:
        
        publish(client)


if __name__ == '__main__':
    run()