#!/usr/bin/env python
import copy

class Dijkstra():
    def __init__(self, VG, start_v, end_v):
        self.v_num = len(VG)
        self.map = copy.deepcopy(VG)
        self.start_v = start_v
        self.end_v = end_v
        self.dis = copy.deepcopy(VG[start_v])
        self.mark = [0]*self.v_num
        self.used = [False]*self.v_num; self.used[0] = True

    def get_path(self):
        path = [self.end_v]
#        print '>>>>>path:',path
#        print 'mark: ', self.mark
        previous_ind = self.mark[self.end_v]
        while not previous_ind == 0:
            path.insert(0, previous_ind)
            previous_ind = self.mark[previous_ind]
        path.insert(0, 0)
        return path
        
    def dijkstra(self):
        if self.start_v == self.end_v: return [self.start_v], 0.0
        for i in range(self.v_num-1):
#            print '>>>>>>>>dis: ', self.dis
#            print 'used: ', self.used
            d_min = float('Inf'); ind = None
            for j in range(self.v_num):
                if not self.used[j] and self.dis[j]<d_min:
                    ind = j; d_min = self.dis[j]
            self.used[ind] = True
            if ind == self.end_v: break
            for j in range(self.v_num):
                if not self.used[j] and self.dis[j]>self.map[ind][j]+d_min:
                    self.dis[j] = self.map[ind][j] + d_min
                    self.mark[j] = ind
        path = self.get_path()
        distance = self.dis[self.end_v]
        return path, distance
