#!/usr/bin/env python
from sklearn.neighbors import KNeighborsClassifier
import pickle
import json
import sys
import os
from os.path import join
from dbhelper import DB

rootpath = os.getenv('WLAN_ROOT')
datapath = join(rootpath,'raw_data')
dbpath = join(datapath,'DB')

def train(dataset):
    db = DB(join(dbpath,'train.db'))
    tbl_manifest = '%s_man'%dataset
    tbl_rss = '%s_rss'%dataset

    n_feature = int(db.queryone('value',tbl_manifest,'key="n_feature"')[0])
    
    data = []
    cls = []
    for y,entry in db.query(['p_id','entry'], tbl_rss):
        dic = json.loads(entry)
        x = [-100]*n_feature
        for m_id,rss in dic.items():
            x[int(m_id)] = float(rss)
        data.append(x)
        cls.append(y)
    neigh = KNeighborsClassifier(n_neighbors=5)
    neigh.fit(data,cls)
    
    fout = open('model.dat','w')
    pickle.dump(neigh,fout)
    fout.close()
