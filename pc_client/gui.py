#!/usr/bin/env python
import pygame
import sys
import Queue
import threading
import time
import socket
import json
from pygame.locals import *
from myuser2 import *
from os.path import join

queue = Queue.Queue(100)
mgr = user_manager()
respath = 'resources'

def gui():
    user_dic = {}
    pygame.init()
    screen = pygame.display.set_mode((1252,582),0,32)
    background = pygame.image.load(join(respath,'map.png')).convert()
    mark = pygame.image.load(join(respath,'mark.png')).convert_alpha()
    mark = pygame.transform.scale(mark,(40,40))
    star = pygame.image.load(join(respath,'star.png')).convert_alpha()
    star = pygame.transform.scale(star,(20,20))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                print 'exit'
                exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    print 'exit'
                    exit(0)
        screen.blit(background,(0,0))
        for uid in mgr.all_users():
            x,y = mgr.get_coord(uid)
            if not x==None:
                screen.blit(mark,(x-20,y-20))
            pid_coord = mgr.pid_coord(uid)
            if not pid_coord == None:
                screen.blit(star,(pid_coord[0]-20,pid_coord[1]-20))
        pygame.display.update()

def receiver():
    global tup
    PORT_LOCAL = 5676
    IP = '127.0.0.1'
    BUFSIZ = 4096
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ss.bind((IP,PORT_LOCAL))
    while True:
        print 'ready to receive'
        info, addr = ss.recvfrom(BUFSIZ)
        state,uid,pid,dir_,speed = json.loads(info)
        mgr.update_user(state,uid,pid,dir_,speed)
        #print state,uid,pid,dir_,speed

def test():
    lst = []
    PORT_GUI = 5676
    for i in range(5):
        time.sleep(5)
        info = (str(i),i,500+i*50,300+i*50,str(i%4+1),10)
        info = json.dumps(info)
        address = ('127.0.0.1', PORT_GUI)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(info, address)
        s.close()

def start():
    thread_rcv = threading.Thread(target=receiver,name='rcv')
    thread_gui = threading.Thread(target=gui,name='gui')
    thread_rcv.daemon = True
    thread_rcv.start()
    thread_gui.start()
#    thread_test = threading.Thread(target=test,name='test')
#    thread_test.daemon = True
#    thread_test.start()

if __name__=='__main__':
    start()
