#!/usr/bin/env python
import threading
import Queue
import socket
import sys
import predictor
import json
import util
from dbhelper import DB

PORT_LOCAL = 5672
PORT_CLIENT = 5674
BUFSIZ = 4096
IP = ""
map_mac = {}
map_pt = {}
db = DB('train.db')

def init():
    global map_mac,map_pt,IP
    IP = util.get_ip('wlan0')
    map_mac = dict([(mac,m_id) for mac,m_id in db.query(['mac','m_id'],'map_mac')])
    map_pt = dict([(p_id,pt) for p_id,pt in db.query(['p_id','pt'],'map_pt')])

def transform(entry):
    dic = json.loads(entry)
    return dict([(map_mac[mac],rss) for mac,rss in dic.items() if mac in map_mac])

def receiver(r_queue):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ss.bind((IP,PORT_LOCAL))
    ss.listen(5)
    while True:
        s,addr = ss.accept()
        ip = addr[0]
        entry = s.recv(BUFSIZ)
        device,entry = entry.split('\t')
        if r_queue.full():
            print 'error: r_queue is full'
            sys.exit()
        r_queue.put((ip,device,entry))
        s.close()

def sender(s_queue):
    while True:
        ip,result = s_queue.get()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,PORT_CLIENT))
        s.send(result)
        s.close()

def processor(r_queue, s_queue):
    while True:
        ip,device,entry = r_queue.get()
        dic = transform(entry)
        #process data
        cls = predictor.predict(dic)
        result = map_pt[cls]
        s_queue.put((ip,result))
        print ip+'\t'+device+'\t'+result


if __name__ == '__main__':
    init()
    r_queue = Queue.Queue(100)
    s_queue = Queue.Queue(100)

    thread_rcv = threading.Thread(target=receiver,name='rcv',args=(r_queue,))
    thread_snd = threading.Thread(target=sender,name='snd',args=(s_queue,))
    thread_pcs = threading.Thread(target=processor,name='pcs',args=(r_queue,s_queue))

    thread_rcv.start()
    thread_snd.start()
    thread_pcs.start()
    
    print '==service started=='
    print 'ip:',IP

