#!/usr/bin/env python
#import sqlite3
import os
import json
import random
from os.path import join
from dbhelper import DB

rootpath = os.getenv('WLAN_ROOT')
datapath = join(rootpath,'raw_data')
dbpath = join(datapath,'DB')

def prepare(dataset):
    split_policy = 'default'
    test_pts = [] #only used when split_policy is 'specify'
    #-------------------------------read data----------------------------
    ratedic = {}
    map_pt = {}
    for txt in os.listdir(join(datapath,dataset,'rss')):
        if not txt in map_pt:
            map_pt[txt] = txt[2:]
        for line in open(join(datapath,dataset,'rss',txt)):
            pt,entry = line.strip().split('\t')
            for item in entry.split(' '):
                mac,rss = item.split('@')
                if not mac in ratedic:
                    ratedic[mac] = 0                
                ratedic[mac] += 1
    mac_lst = [mac for mac,rate in ratedic.items() if rate > 500]
    map_mac = dict([(mac,i) for i,mac in enumerate(mac_lst)])
    map_coord = {}
    for line in open(join(datapath,dataset,'map','coord.txt')):
        pt,xy = line.strip().split('\t')
        x,y = xy.split(' ')
        map_coord[pt] = (x,y)
    relation_lst = []
    for line in open(join(datapath,dataset,'map','relation.txt')):
        src,dest,dist,dir_ = line.strip().split('\t')
        relation_lst.append((map_pt[src],map_pt[dest],dist,dir_))
    #-------------------------------store data----------------------------
    db = DB(join(dbpath,'raw.db'))
    tbl_mac = '%s_mac'%dataset
    tbl_pt = '%s_pnt'%dataset
    tbl_relation = '%s_rel'%dataset
    tbl_manifest = '%s_man'%dataset
    tbl_rss = '%s_rss'%dataset

    # [dataset]_mac : ( m_id | mac )
    db.new_table(tbl_mac, ('m_id integer','mac text'))
    db.insertmany([ (m_id,mac) for mac,m_id in map_mac.items()], tbl_mac)
    # [dataset]_pnt : ( p_id | pt | x | y )
    db.new_table(tbl_pt, ('p_id integer','pt text','x real','y real'))
    db.insertmany([(p_id,pt)+map_coord[pt] for pt,p_id in map_pt.items()], tbl_pt)
    #[dataset]_rel: ( src_pt | dest_pt | distance | directions )
    db.new_table(tbl_relation, ('src_pt integer','dest_pt integer','distance real','directions text'))
    db.insertmany(relation_lst, tbl_relation)
    # [dataset]_manifest : (key, value)
    db.new_table(tbl_manifest, ('key text','value text'))
    db.insert(('n_feature',len(map_mac)), tbl_manifest)
    db.insert(('n_point',len(map_pt)), tbl_manifest)
    
#    for device in os.listdir(join(datapath,dataset)):
    r_id = 0
    db.insert(('dataset',tbl_rss), tbl_manifest)
    #[dataset]_rss: ( r_id | p_id | entry )
    db.new_table(tbl_rss, ('r_id integer','p_id integer','entry text'))
    for txt in os.listdir(join(datapath,dataset,'rss')):
        for line in open(join(datapath,dataset,'rss',txt)):
            r_id += 1
            dic = {}
            pt,entry = line.strip().split('\t')
            for item in entry.split(' '):
                mac,rss = item.split('@')
                if not mac in map_mac:  #filter
                    continue
                dic[map_mac[mac]] = rss
            entry = json.dumps(dic)
            db.insert((r_id, map_pt[pt], entry), tbl_rss)

    db.new_table('meta', ('key text','value text'))
    db.insert(('current',dataset),'meta')

    db.commit()
                
    #-------------------------------split data----------------------------
    db_train = DB(join(dbpath,'train.db'))
    db_test = DB(join(dbpath,'test.db'))
#    for device in db.queryone('value', 'manifest', 'key="device"'):
    db_train.new_table(tbl_rss, ('r_id integer','p_id integer','entry text'))
    db_test.new_table(tbl_rss, ('r_id integer','p_id integer','entry text'))
    if split_policy == None:
        #no test data
        db_train.clone_from(db, tbl_rss)
    elif split_policy == 'default':
        #70% train data & 30% test data
        for record in db.queryall(tbl_rss):
            if random.random() > 0.3:
                db_train.insert(record, tbl_rss)
            else:
                db_test.insert(record, tbl_rss)
    elif split_policy == 'specify':
        #user specify
        for record in db.queryall(tbl_rss):
            if record[1] in test_pts:
                db_test.insert(record, tbl_rss)
            else:
                db_train.insert(record, tbl_rss)
    else:
        #error
        pass
    
    db_train.clone_from(db, tbl_manifest)
    db_train.clone_from(db, tbl_mac)
    db_train.clone_from(db, tbl_pt)
    db_train.clone_from(db, tbl_relation)
    db_train.clone_from(db, 'meta')
    
    db_test.clone_from(db, tbl_manifest)
    db_test.clone_from(db, tbl_mac)
    db_test.clone_from(db, tbl_pt)
    db_test.clone_from(db, tbl_relation)
    db_test.clone_from(db, 'meta')

    
    db_train.commit()
    db_test.commit()

    

if __name__=='__main__':
    prepare()
