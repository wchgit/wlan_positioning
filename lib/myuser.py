#!/usr/bin/env python
import util
import time
import building as bd
from dbhelper import DB
import dijkstra as dij

class user(object):
    '''
    user info
    '''
    def __init__(self, uid):
        self.uid = uid
        #self.timestamp = time.time()
        self.timestamp = 1401724835.417 #for testing
        self.history = []
        self.cnt = 0
        self.time_ = 0.0
        self.speed = 4.0
        self.dist = 0.0
        self.stride = 0.0
        self.dir_ = None
        self.is_walking = False
        self.dir_changed = False
        self.pid_changed = False
        self.walk_changed = False
    def update(self, step_seq, timestamp, pid):
        #state check
        if step_seq!=[]:
            self.is_walking = True
        else:
            self.is_walking = False
            print '='*30,pid,'stoped'
        if step_seq!=[] and self.dir_ != self.get_dir(step_seq[-1]):
            self.dir_changed = True
            print '='*30,pid,'direction changed'
        else:
            self.dir_changed = False
        if self.history == []:
            self.pid_changed = True
            print '='*30,pid,'pid changed'
        elif self.history != [] and self.vote(self.history) != self.vote(self.history+[pid]):
            self.pid_changed = True
            print '='*30,pid,'pid changed'
        else:
            self.pid_changed = False
        #check wether pid possible
        if self.pid_changed and self.history!=[]:
            dir_ = self.dir_
            if self.dir_changed:
                dir_ = self.get_dir(step_seq[-1])
            if not self.pid_possible(dir_,self.history[-1],pid):
                self.is_walking = False
                self.dir_changed = False
                self.pid_changed = False
                print '='*30,pid,'impossible'
                return
        #update
        num = len(step_seq)
        self.cnt += num
        self.dist += self.calc_dist(pid)
        if not step_seq == []:
            self.dir_ = self.get_dir(step_seq[-1])
        if not self.cnt == 0:
            self.stride = self.dist/self.cnt
        if self.is_walking:
            self.time_ += timestamp-self.timestamp
            self.timestamp = timestamp
        if self.time_>0 and self.dist>0:
            self.speed = self.dist/self.time_
        self.history.append(pid)
    def pid_possible(self,dir_,last,pid):
        #pid_possible enabled
#        x_,y_ = bd.get_coordinate(last)
#        x,y = bd.get_coordinate(pid)
#        if dir_==1 and x-x_>30:
#            return True
#        elif dir_==2 and y-y_>30:
#            return True
#        elif dir_==3 and x_-x>30:
#            return True
#        elif dir_==4 and y_-y>30:
#            return True
#        else:
#            return False
        #pid_possible disabled
        return True
    def get_dir(self,angle):
        angle = float(angle)
        if angle<45 or angle>=315:
            return 4
        elif angle>=45 and angle<135:
            return 1
        elif angle>=135 and angle<225:
            return 2
        elif angle>=225 and angle<315:
            return 3
    def calc_dist(self, pid):
        '''
        calculate distance between current point and last point
        current point -> result
        last point -> history[-1] if history has more than one element
        using Dijkstra algorithm
        '''
        if self.history == []:
            return 0.0
        A = bd.get_p2pdistance()
        p1,p2 = self.history[-1],pid
        di = dij.Dijkstra(A, p1, p2)
        path, distance = di.dijkstra()
        return distance
    def vote(self,lst):
        #vote enabled
#        last = lst[-3:]
#        s = set(last)
#        max_,ind = 0,0
#        for i in s:
#            if last.count(i) > max_:
#                max_ = last.count(i)
#                ind = i
#        return lst[i]
        #vote disabled
        return lst[-1]
    def get_info(self):
        state = [self.is_walking,self.dir_changed,self.pid_changed]
        print state
        pid = self.vote(self.history)
        return state,self.uid,pid,self.dir_,self.speed

class user_manager(object):
    def __init__(self):
        self.dic = {}
    def get_user(self,uid):
        if not self.dic.has_key(uid):
            self.dic[uid] = user(uid)
        return self.dic[uid]
    def population(self):
        return len(self.dic)


if __name__=='__main__':
    mgr = user_manager()
    u = mgr.get_user('1234567')
    u.update([1,2,2,3,4],time.time(),0)
    #u.update([3,3,3],time.time(),2)
    u.update([3,3,3],time.time(),3)
