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
                    #t = datetime.datetime.fromtimestamp(packet['rxTime']).strftime('%Y-%m-%d %H:%M:%S')
                    t = packet['rxTime']
                except KeyError:
                    #print('Time error')
                    t = time.time()
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
                    t = packet['rxTime']
                except KeyError:
                    #print('Time error')
                    t = time.time()
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
                    t = packet['rxTime']
                except KeyError:
                    #print('Time error')
                    t = time.time()
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


if __name__ == "__main__":
    #from meshlib import *
    # https://python.meshtastic.org/mesh_interface.html

    client = MeshtasticClient('/dev/ttyACM0')
    client.meshint.getMyNodeInfo()
    client.checkMail()
    client.meshint.sendText("Test", wantAck=True)
    client.meshint.sendText("DM Test", destinationId='!xxxxxx', wantAck=True)
    client.meshint.sendPosition(latitude=45, longitude=-73, altitude=20, wantAck=True)
    client.meshint.sendData(b'[TestData]',portNum=258, wantAck=True) #256-511 for private apps
    client.meshint.sendPosition(latitude=0.0, longitude=0.0, altitude=0, timeSec=0, destinationId='^all', wantAck=False, wantResponse=False)
    client.meshint.close()

    #client.meshint.sendText(
    # text: str, 
    # destinationId: Union[int, str] = '^all', 
    # wantAck: bool = False, 
    # wantResponse: bool = False, 
    # onResponse: Optional[Callable[[dict], Any]] = None, 
    # channelIndex: int = 0)

    #client.meshint.sendPosition(
    # latitude: float = 0.0, 
    # longitude: float = 0.0, 
    # altitude: int = 0, 
    # destinationId: Union[int, str] = '^all', 
    # wantAck: bool = False, 
    # wantResponse: bool = False, 
    # channelIndex: int = 0)

    #client.meshint.sendData(
    # data, 
    # destinationId: Union[int, str] = '^all', 
    # portNum: int = 256, 
    # wantAck: bool = False, 
    # wantResponse: bool = False, 
    # onResponse: Optional[Callable[[dict], Any]] = None, 
    # onResponseAckPermitted: bool = False, 
    # channelIndex: int = 0, 
    # hopLimit: Optional[int] = None, 
    # pkiEncrypted: Optional[bool] = False, 
    # publicKey: Optional[bytes] = None)

    """Keyword Arguments: data – the data to send, either as an array of bytes or as a protobuf (which will be automatically serialized to bytes) destinationId {nodeId or nodeNum} – where to send this message (default: {BROADCAST_ADDR}) portNum – the application portnum (similar to IP port numbers) of the destination, see portnums.proto for a list wantAck – True if you want the message sent in a reliable manner (with retries and ack/nak provided for delivery) wantResponse – True if you want the service on the other side to send an application layer response onResponse – A closure of the form funct(packet), that will be called when a response packet arrives (or the transaction is NAKed due to non receipt) onResponseAckPermitted – should the onResponse callback be called for regular ACKs (True) or just data responses & NAKs (False) Note that if the onResponse callback is called 'onAckNak' this will implicitly be true. channelIndex – channel number to use hopLimit – hop limit to use"""

