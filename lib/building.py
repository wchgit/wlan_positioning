#!/usr/bin/env python
from dbhelper import DB
import json
from os.path import join
import os

rootpath = os.getenv('WLAN_ROOT')
datapath = join(rootpath,'raw_data')
dbpath = join(datapath,'DB')
db = DB(join(dbpath,'train.db'))
dataset = db.queryone('value','meta','key="current"')[0]
tbl_mac = '%s_mac'%dataset
tbl_pt = '%s_pnt'%dataset
tbl_relation = '%s_rel'%dataset
tbl_manifest = '%s_man'%dataset
tbl_rss = '%s_rss'%dataset

map_mac = {}
map_pt = {}
feas_map = {}
mac_dic = dict([(mac,m_id) for mac,m_id in db.query(['mac','m_id'],tbl_mac)])
pid_dic = dict([(p_id,pt) for p_id,pt in db.query(['p_id','pt'],tbl_pt)])
coord_dic = dict([(p_id,(int(x),int(y))) for p_id,x,y in db.query(['p_id','x','y'],tbl_pt)])
n_point = int(db.queryone('value',tbl_manifest,'key="n_point"')[0])
p2p_matrix = [[float('inf')]*n_point for i in range(n_point)]
for i in range(n_point):
    p2p_matrix[i][i] = 0.0
for i,j,dis in db.query(['src_pt','dest_pt','distance'],tbl_relation):
    p2p_matrix[i][j] = p2p_matrix[j][i] = dis

def get_macid(mac):
    return mac_dic[mac]

def get_pointname(pid):
    return pid_dic[pid]

def get_coordinate(pid):
    return coord_dic[pid]

def has_mac(mac):
    return mac in mac_dic

def transform(entry):
    dic = json.loads(entry)
    return dict([(get_macid(mac),rss) for mac,rss in dic.items() if has_mac(mac)])

pt_dic = dict([(pt,p_id) for p_id,pt in db.query(['p_id','pt'],tbl_pt)])
mid_dic = dict([(m_id,mac) for mac,m_id in db.query(['mac','m_id'],tbl_mac)])
def retransform(entry):
    dic = json.loads(entry)
    dic = dict([(mid_dic[int(m_id)],float(rss)) for m_id,rss in dic.items()])
    return json.dumps(dic)

def get_p2pdistance():
    return p2p_matrix

def nearest_neighbor(x,y):
    target = -1
    min_ = float('inf')
    for pid,(x_,y_) in coord_dic.items():
        dist = (x-x_)**2+(y-y_)**2
        if dist<min_:
            min_ = dist
            target = (pid,x_,y_)
    return target
