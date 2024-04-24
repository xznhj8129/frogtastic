import datetime
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import time

def onConnection(id, interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    interface.sendText("Node {} Online".format(self.id))

class MeshtasticClient():
    def __init__(self, device):
        self.rec = None
        self.new = False
        self.rect = 0
        self.packet = None
        self.maxlen = 240
        #print(meshtastic.serial_interface)
        self.meshint = meshtastic.serial_interface.SerialInterface(device)
        myinfo = self.meshint.getMyUser()
        self.id = myinfo['id']
        
        self.messages = []
        pub.subscribe(self.onReceive, "meshtastic.receive")

    def onReceive(self, packet, interface): # called when a packet arrives
        #print(f"Received: {packet}")
        try:
            snr = packet['rxSnr']
        except KeyError:
            snr = None
        try:
            rssi = packet['rxRssi']
        except KeyError:
            rssi = None
        sender = packet['fromId']
        self.packet = packet
        self.rect = time.time()
        if packet['decoded']['portnum']=='TEXT_MESSAGE_APP':
            try:
                try:
                    if 'altitude' in packet['decoded']['position'].keys():
                        pos = (packet['decoded']['position']['latitude'], packet['decoded']['position']['longitude'], packet['decoded']['position']['altitude'])
                    else:
                        pos = (packet['decoded']['position']['latitude'], packet['decoded']['position']['longitude'], 0)
                except KeyError:
                    #print('Pos error')
                    pos = None
                try:
                    longname = interface.nodes[sender]['user']['longName']
                except KeyError:
                    #print('Sender error')
                    longname = None
                try:
                    t = datetime.datetime.fromtimestamp(packet['rxTime']).strftime('%Y-%m-%d %H:%M:%S')
                except KeyError:
                    #print('Time error')
                    t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                self.rec = {
                    'senderid': sender,
                    'sender': longname,
                    'type': 'TEXT_MESSAGE_APP',
                    'port': None,
                    'pos': pos,
                    'snr': snr,
                    'rssi': rssi,
                    'dest': packet['toId'],
                    'time': t,
                    'data': packet['decoded']['text']
                }
                #print(self.rec)
                self.messages.append(self.rec)
                self.new = True
            
            except Exception as e:
                print('=========================================')
                print('Error')
                print(packet)
                print(e)
                print('=========================================')

        elif packet['decoded']['portnum']=='POSITION_APP':
            try:
                try:
                    if 'altitude' in packet['decoded']['position'].keys():
                        pos = (packet['decoded']['position']['latitude'], packet['decoded']['position']['longitude'], packet['decoded']['position']['altitude'])
                    else:
                        pos = (packet['decoded']['position']['latitude'], packet['decoded']['position']['longitude'], 0)
                    #print("Position {} {}".format(sender,senderpos))
                except KeyError:
                    #print('Pos error')
                    pos = None
                try:
                    longname = interface.nodes[sender]['user']['longName']
                except KeyError:
                    #print('Sender error')
                    longname = None
                try:
                    t = datetime.datetime.fromtimestamp(packet['rxTime']).strftime('%Y-%m-%d %H:%M:%S')
                except KeyError:
                    #print('Time error')
                    t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                self.rec = {
                    'senderid': sender,
                    'sender': longname,
                    'type': 'POSITION_APP',
                    'port': None,
                    'pos': pos,
                    'snr': snr,
                    'rssi': rssi,
                    'dest': packet['toId'],
                    'time': t,
                    'data': None
                }
                #print(self.rec)
                self.messages.append(self.rec)
                self.new = True
            
            except Exception as e:
                print('=========================================')
                print('Error')
                print(packet)
                print(e)
                print('=========================================')

        elif packet['decoded']['portnum']=='PRIVATE_APP' or type(packet['decoded']['portnum']) is int:
            try:  
                try:
                    longname = interface.nodes[sender]['user']['longName']
                except KeyError:
                    #print('Sender error')
                    longname = None
                try:
                    t = datetime.datetime.fromtimestamp(packet['rxTime']).strftime('%Y-%m-%d %H:%M:%S')
                except KeyError:
                    #print('Time error')
                    t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                self.rec = {
                    'senderid': sender,
                    'sender': longname,
                    'type': 'PRIVATE_APP',
                    'port': packet['decoded']['portnum'],
                    'snr': snr,
                    'rssi': rssi,
                    'pos': None,
                    'dest': packet['toId'],
                    'time': t,
                    'data': packet['decoded']['payload']
                }
                #print(self.rec)
                self.messages.append(self.rec)
                self.new = True
            
            except Exception as e:
                print('=========================================')
                print('Error')
                print(packet)
                print(e)
                print('=========================================')

    def checkMail(self):
        if self.new:
            self.new = False
            msgs = self.messages
            self.messages = []
            return msgs

    def getPosition(self):
        a = client.meshint.getMyNodeInfo()
        if 'altitude' in a['position'].keys():
            return (a['position']['latitude'], a['position']['longitude'], a['position']['altitude'])
        else:
            return (a['position']['latitude'], a['position']['longitude'], 0)

