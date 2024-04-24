from meshlib import *
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
