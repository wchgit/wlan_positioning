#!/usr/bin/env python
import threading
import Queue
import socket
import sys
import predictor
import json
from datetime import *
import logging
import time
from myuser import *
import building as bd
import util

PORT_LOCAL = 5672
PORT_CLIENT = 5674
PORT_GUI = 5676
#IP = util.get_ip('wlan0')
IP = '127.0.0.1'

r_queue = Queue.Queue(100)
s_queue = Queue.Queue(100)
gui_queue = Queue.Queue(100)
umgr = user_manager()

def processor():
    last = None
    while True:
        ip,uid,step_seq,timestamp,entry = r_queue.get()
        entry = bd.transform(entry)
        proba = predictor.predict(entry)
        pid = proba.index(max(proba))
        coord = bd.get_coordinate(pid)
        pt = bd.get_pointname(pid)

        usr = umgr.get_user(uid)
        usr.update(step_seq,timestamp,pid)

        s_queue.put((ip,pt))
        gui_queue.put(usr)
        print ip+'\t'+pt

def gui_sender():
    while True:
        usr = gui_queue.get()
        info = usr.get_info()
        if info == None:
            continue
        info = json.dumps(info)
        address = ('127.0.0.1', PORT_GUI)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(info, address)
        s.close()

def sender(): #udp
    while True:
        ip,result = s_queue.get()
        address = (ip, PORT_CLIENT)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(result, address)
        s.close()

def receiver(): #udp
    BUFSIZ = 4096
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ss.bind((IP,PORT_LOCAL))
    while True:
        print '-'*20+'>'*20
        entry, addr = ss.recvfrom(BUFSIZ)
        ip = addr[0]
        uid,step_seq,entry,timestamp = entry.split('\t')
        step_seq = [str(i) for i in json.loads(step_seq)]
        if r_queue.full():
            logging.error('damn it! r_queue is full!!!')
            sys.exit()
        r_queue.put((ip,uid,step_seq,float(timestamp)/1000,entry))

def test():
    rootpath = os.getenv('WLAN_ROOT')
    datapath = join(rootpath,'raw_data')
    dbpath = join(datapath,'DB')

    start = time.time()
    for line in open('test1.log'):
        time.sleep(1)
        uid,step_seq,entry,timestamp = line.strip().split('\t')
        timestamp = float(timestamp)
        address = (IP, PORT_LOCAL)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(line.strip(), address)
        s.close()

def start():
    logging.basicConfig(filename='log',format='%(levelno)d %(asctime)s\t%(message)s',level=logging.DEBUG)

    thread_lst = []
    thread_lst.append(threading.Thread(target=receiver,name='rcv',args=()))
    thread_lst.append(threading.Thread(target=sender,name='snd',args=()))
    thread_lst.append(threading.Thread(target=gui_sender,name='guisnd',args=()))
    thread_lst.append(threading.Thread(target=processor,name='pcs',args=()))

    for thread in thread_lst:
        thread.start()
    
    print '==service started=='
    print 'ip:',IP
    
    #threading.Thread(target=test,name='test',args=()).start()

if __name__ == '__main__':
    start()

#---------------------->>>>>>>>>>>>>>>>>>>>TCP SENDER
'''
def sender(s_queue):
    while True:
        ip,result = s_queue.get()
        address = (ip, PORT_CLIENT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(address)
            s.send(result)
        except Exception as e:
            logging.error('damn it! network ungeilivable!!!')
            s.close()
            continue
        s.close()
'''

#---------------------->>>>>>>>>>>>>>>>>>>>TCP RECEIVER
'''
def receiver(r_queue):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ss.bind((IP,PORT_LOCAL))
    ss.listen(1)
    while True:
        s,addr = ss.accept()
        entry = s.recv(BUFSIZ)
        ip = addr[0]
        print entry
        print time.time()
        s.close()

        device,step_seq,entry,timestamp = entry.split('\t')
        step_seq = [str(i) for i in json.loads(step_seq)]
        if r_queue.full():
            logging.error('damn it! r_queue is full!!!')
            sys.exit()
        r_queue.put((ip,device,step_seq,entry))
'''
