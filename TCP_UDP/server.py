import socket
import struct,time,array
import requests

ip_addr = socket.gethostbyname(socket.gethostname())
UDP_IP = ip_addr
UDP_PORT = 1005
MESSAGE = "Hi, can you listen to this?"

print("server start\n")
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
            print("received in server\n")
    else:
        print("did not receive in server \n")

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


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    seq_old = seq_new
    ack_old = ack_new
    old_length = new_length 

    pack=TCPPacket(seq_old,ack_old,MESSAGE).build()
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data = data.decode('utf-8')

    c,seq_n,ack_n,m = checkdata(data)
   
    if(c == 1):
        print(m)
        seq_new = ack_old
        ack_new = seq_old + len(m)
        new_length = len("received")
        packet_new = TCPPacket(seq_new,ack_new,"received").build()
        sock.sendto(packet_new.encode('utf-8'), addr)
        ack_new = seq_new + new_length
    else:
        sock.sendto(pack.encode('utf-8'), addr)
        new_length = len(MESSAGE)
        ack_new = seq_old + new_length
    sock.sendto(pack.encode('utf-8'), addr)
    new_length = len(MESSAGE)
    ack_new = seq_old + new_length