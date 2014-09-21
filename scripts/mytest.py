import os
from os.path import join
import time
import socket

PORT_SERVER = 5672
IP = '127.0.0.1'


def test(dataset):
    rootpath = os.getenv('WLAN_ROOT')
    datapath = join(rootpath,'raw_data')

    start = time.time()
    for line in open(join(datapath,dataset,'test','test.log')):
        time.sleep(1)
        uid,step_seq,entry,timestamp = line.strip().split('\t')
        timestamp = float(timestamp)
        address = (IP, PORT_SERVER)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(line.strip(), address)
        s.close()

if __name__ == '__main__':
    test()
