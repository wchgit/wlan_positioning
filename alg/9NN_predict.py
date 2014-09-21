#!/usr/bin/env python
import pickle
from dbhelper import DB
import os
from os.path import join

rootpath = os.getenv('WLAN_ROOT')
datapath = join(rootpath,'raw_data')
dbpath = join(datapath,'DB')
db = DB(join(dbpath,'train.db'))
dataset = db.queryone('value','meta','key="current"')[0]
tbl_manifest = '%s_man'%dataset
n_feature = int(db.queryone('value',tbl_manifest,'key="n_feature"')[0])

fin = open('model.dat')
clf = pickle.load(fin)
fin.close

def predict(dic):
    data = [-100]*n_feature
    for m_id, rss in dic.items():
        data[int(m_id)] = float(rss)
    proba = clf.predict_proba([data]).tolist()[0]
    return proba
