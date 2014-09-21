#!/usr/bin/env python
import sys
import os
from os.path import join,abspath,dirname

rootpath = dirname(abspath(__file__))
os.environ['WLAN_ROOT'] = rootpath
envpath = join(rootpath,'pc_client')
libpath = join(rootpath,'lib')

sys.path.append(libpath)
sys.path.append(envpath)

def pc_client():
    os.chdir(envpath)
    import gui
    gui.start()

if __name__=='__main__':
    pc_client()
