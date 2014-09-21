#!/usr/bin/env python
import sys
import shutil
import os
import os.path
from os.path import join,abspath,dirname,exists
import getopt

rootpath = dirname(abspath(__file__))
os.environ['WLAN_ROOT']=rootpath
envpath = join(rootpath,'env')
libpath = join(rootpath,'lib')
datapath = join(rootpath,'raw_data')
sys.path.append(libpath)
sys.path.append(envpath)

def build_env(dataset,alg):
    #remove old files
    shutil.rmtree(envpath,True)
    os.mkdir(envpath)
    #copy scripts to target dir
    shutil.copytree(join(rootpath,'raw_data'),join(envpath,'raw_data'))
    shutil.copy(join(rootpath,'alg','%s_train.py'%alg),join(envpath,'train.py'))
    shutil.copy(join(rootpath,'alg','%s_predict.py'%alg),join(envpath,'predictor.py'))
    scripts=[
        'prepare.py',
        'server.py',
        'mytest.py',
    ]
    for src in scripts:
        shutil.copy(join(rootpath,'scripts',src),envpath)
    #go to target dir
    os.chdir(envpath)

def start_offline(dataset):
    #sys.path.append(envpath)
    os.chdir(envpath)
    import prepare
    prepare.prepare(dataset)
    import train
    train.train(dataset)

def start_online():
    #sys.path.append(envpath)
    os.chdir(envpath)
    import server
    server.start()

def start_test(dataset):
    os.chdir(envpath)
    import mytest
    mytest.test(dataset)
    
if __name__=='__main__':
    usage_str="""
    usage:
      $./go.py -d dataset -a alg
      $./go.py -d dataset -a alg env
      $./go.py offline
      $./go.py online
    """
    dataset=None
    alg=None
    env=offline=online=False
    opts, args = getopt.getopt(sys.argv[1:], "hd:a:")

    opts = dict(opts)
    dataset = opts['-d'] if '-d' in opts else None
    alg = opts['-a'] if '-a' in opts else None
    usage = True if '-h' in opts else False

    env = True if 'env' in args else False
    offline = True if 'offline' in args else False
    online = True if 'online' in args else False
    test = True if 'test' in args else False
    if(env==False and offline==False and online==False and test==False):
        env=offline=online=True

    if usage:
        print usage_str
        sys.exit(0)

    if env:
        if dataset==None or alg==None:
            raise Exception('use -d and -a when build env')
        if not exists(join(datapath,dataset)):
            raise Exception('dataset does not exist')
        if not exists(join(rootpath,'alg','%s_train.py'%alg)):
            raise Exception('algothrithm does not exist')
        build_env(dataset, alg)

    if offline:
        if not exists(envpath):
            raise Exception('environment not found')
        os.chdir(envpath)
        start_offline(dataset)
    if online:
        model_path=join(envpath,'model.dat')
        if not exists(model_path):
            raise Exception('model not found')
        os.chdir(envpath)
        start_online()
    if test:
        if not exists(envpath):
            raise Exception('environment not found')
        if dataset==None:
            raise Exception('use -d [dataset] test')
        if not exists(join(datapath,dataset)):
            raise Exception('dataset does not exist')
        os.chdir(envpath)
        start_test(dataset)
