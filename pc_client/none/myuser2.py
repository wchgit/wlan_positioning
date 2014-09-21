#!/usr/bin/env python
import time
import building as bd
import math

class user(object):
    '''
    user info
    '''
    def __init__(self, uid):
        self.uid = uid
        self.timestamp = time.time()
        self.pid = None
        self.x = None
        self.y = None
        self.speed = 5.0
        self.dir_ = None
        self.is_walking = False
    def update(self,state,pid,dir_,speed):
        '''
        state[0]->is_walking
        state[1]->dir_changed
        state[2]->pid_changed
        '''
        x,y = bd.get_coordinate(pid)
#        if state[0]==True:
#            #self.speed = speed
#            self.speed = 4.0
#        else:
#            self.speed = 0.0
        self.speed_control(x,y)
        if state[1]==True:
            pid,x_,y_ = bd.nearest_neighbor(x,y)
            self.x = x_
            self.y = y_
            self.dir_ = dir_
            print '='*30,'dir change, coord adjusted'
        if state[2]==True:
            if self.x == None:
                self.x = x
                self.y = y
            self.pid = pid
    def speed_control(self,x,y):
        #speed_control enabled
        if self.dir_ == None:
            return
        behand = True
        if self.dir_==1 and self.x>=x:
            behand = False
        if self.dir_==2 and self.y>=y:
            behand = False
        if self.dir_==3 and self.x<=x:
            behand = False
        if self.dir_==4 and self.y<=y:
            behand = False
        dis = math.sqrt((self.x-x)**2+(self.y-y)**2)
        if behand and self.speed<10:
            self.speed = self.speed+dis*0.003
            print '='*30,'speed up',self.speed
        if behand==False and self.speed>3:
            self.speed = self.speed-dis*0.003
            print '='*30,'speed down',self.speed
        #speed_control disabled
        #pass
    def autoupdate(self):
        current = time.time()
        delta = (current-self.timestamp)
        self.timestamp = current
        if self.dir_ == 1:
            self.x += self.speed*delta
        elif self.dir_ == 2:
            self.y += self.speed*delta
        elif self.dir_ == 3:
            self.x -= self.speed*delta
        elif self.dir_ == 4:
            self.y -= self.speed*delta
    def get_coord(self):
        if self.pid!=None:
            x,y = bd.get_coordinate(self.pid)
            r = math.sqrt((self.x-x)**2+(self.y-y)**2)
            self.autoupdate()
#            if r<100:
#                self.autoupdate()
#            else:
#                print '='*30,'out of range, stop update'
#                pass
        return self.x,self.y

class user_manager(object):
    def __init__(self):
        self.dic = {}
    def update_user(self,state,uid,pid,dir_,speed):
        if not self.dic.has_key(uid):
            self.dic[uid] = user(uid)
        self.dic[uid].update(state,pid,dir_,speed)
    def all_users(self):
        return self.dic.keys()
    def get_coord(self,uid):
        return self.dic[uid].get_coord()
    def pid_coord(self,uid):
        pid = self.dic[uid].pid
        if pid == None:
            return None
        return bd.get_coordinate(pid)

if __name__=='__main__':
    mgr = user_manager()
    u = mgr.update_user('1234567',1,1,1,100)
    u = mgr.update_user('1234',3,4,1,100)
    for uid in mgr.all_users():
        x,y = mgr.get_coord(uid)
        print uid,x,y

