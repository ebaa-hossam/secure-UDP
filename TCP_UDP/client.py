import socket
import struct,time,array
import requests

ip_addr = socket.gethostbyname(socket.gethostname())
UDP_IP = ip_addr
UDP_PORT = 1005
MESSAGE = "Hi, can you listen to this?"

seq_old=0
ack_old=0
seq_new=0
ack_new=0
old_length=0
new_length=len(MESSAGE)

delimiter='(****)'
def chksum(packet) :
    array= packet.split(delimiter)
    Checksum = str(array[0]) + str(array[1]) + str(array[2])
    return Checksum

def checkdata(data) :
    c=0
    array = data.split(delimiter)
    checksum = array[0]
    seq_n = array[1]
    ack_n = array[2]
    message = array[3]
    checksum_n = str(seq_n) + str(ack_n) + str(message)
    if(checksum == checksum_n):
        if(ack_n == str(seq_old + old_length)):
            c=1
            print("received in client\n")
    else:
        print("did not receive in client \n")        
    return c,seq_n,ack_n,message

class TCPPacket:
    def __init__(self,
                 seq_n:  int,
                 ack_n:  int,
                 message:   str):
        self.seq_n = seq_n
        self.ack_n = ack_n
        self.message = message

    def build(self) -> bytes:
        packet = str(self.seq_n) + delimiter + str(self.ack_n) + delimiter + str(self.message)
        check = chksum (packet)
        packet = str(check) + delimiter + packet
        return packet
    
def GETrequest(url):
   URL = url
   x = requests.get(URL)
   print(x.status_code)
   print("get\n")
    
def POSTrequest(URL,MYOBJ):
    url = URL
    myobj = MYOBJ
    x = requests.post(url, json = myobj)
    print(x.text)
    print("post\n")
    
print("client start\n")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(MESSAGE)

GETrequest('https://w3schools.com')
POSTrequest('https://www.w3schools.com/python/demopage.php', {'somekey': 'somevalue'})

while True:
    seq_old = seq_new
    ack_old = ack_new
    
    pack=TCPPacket(seq_old,ack_old,MESSAGE).build()
    sock.sendto(pack.encode('utf-8'), (UDP_IP, UDP_PORT))
    old_length = len(MESSAGE)

    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data = data.decode('utf-8')

    c,seq_n,ack_n,m = checkdata(data)
    if(c == 1):
        seq_new = ack_old
        ack_new = seq_old + len(m)
        packet_new = TCPPacket(seq_new,ack_new,"received").build()
        old_length = len("received")
        sock.sendto(packet_new.encode('utf-8'), addr)
        ack_new = seq_new + old_length
        print(m)
    else:
        
        sock.sendto(pack.encode('utf-8'), addr)
        old_length = len(MESSAGE)
        ack_new = seq_old + old_length
