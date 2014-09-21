#!/usr/bin/env python
import pygame
import sys
from pygame.locals import *
import Tkinter as tk
import math

class input_dialog():
    def __init__(self,x,y):
        self.pt = None
        self.x = x
        self.y = y
        self.win = tk.Tk()
        self.win.geometry('+%d+%d'%(500,300))
        
        tk.Label(self.win,text='x').grid(row=0,column=0)
        tk.Button(self.win,text='-',command=self.minusx).grid(row=0,column=1)
        self.xval = tk.Label(self.win,text=str(self.x))
        self.xval.grid(row=0,column=2)
        tk.Button(self.win,text='+',command=self.addx).grid(row=0,column=3)

        tk.Label(self.win,text='y').grid(row=1,column=0)
        tk.Button(self.win,text='-',command=self.minusy).grid(row=1,column=1)
        self.yval = tk.Label(self.win,text=str(self.y))
        self.yval.grid(row=1,column=2)
        tk.Button(self.win,text='+',command=self.addy).grid(row=1,column=3)
        
        tk.Label(self.win,text='p').grid(row=2,column=0)
        self.entry = tk.Entry(self.win)
        self.entry.grid(row=2,column=1,columnspan=3)
        self.entry.focus_set()

        tk.Button(self.win,text='OK',command=self.ok).grid(row=3,columnspan=2)
        tk.Button(self.win,text='cancel',command=self.cancel).grid(row=3,column=2,columnspan=2)

    def show(self):
        tk.mainloop()
    def cancel(self):
        self.win.destroy()
    def ok(self):
        self.pt = self.entry.get()
        self.win.destroy()
    def addx(self):
        self.x += 1
        self.xval.config(text=str(self.x))
    def minusx(self):
        self.x -= 1
        self.xval.config(text=str(self.x))
    def addy(self):
        self.y += 1
        self.yval.config(text=str(self.y))
    def minusy(self):
        self.y -= 1
        self.yval.config(text=str(self.y))
    def get(self):
        if self.pt == None:
            return (None,None,None)
        return (self.pt,self.x,self.y)


class mark():
    def __init__(self):
        self.mark = pygame.image.load('star.png').convert_alpha()
        self.mark = pygame.transform.scale(self.mark,(30,30))
    def getone(self):
        return self.mark.copy()

def neighbor((x,y),mark_lst):
    lst = [(x-xi)**2+(y-yi)**2 for xi,yi,pt,m in mark_lst]
    x,y,pt = mark_lst[lst.index(min(lst))][:3]
    return (x,y),pt

def direction(x,y,x_,y_):
    #before:x,y   after:x_,y_
    direction = ''
    if abs(x_-x) > abs(y_-y):
        if x_-x>0:
            direction = 'E'
        else:
            direction = 'W'
        y_ = y
    else:
        if y_-y>0:
            direction = 'S'
        else:
            direction = 'W'
        x_ = x
    return direction,x_,y_

def distance(x,y,x_,y_):
    return math.sqrt((x-x_)**2+(y-y_)**2)

def relation_info(point_lst,mark_lst,line_lst):
    if len(point_lst) < 2:
        return None
    new_point_lst = []
    src,src_pt = neighbor(point_lst.pop(0),mark_lst)
    dest,dest_pt = neighbor(point_lst.pop(),mark_lst)
    point_lst.append(dest)
    directions = []
    dist = 0
    last = src
    new_point_lst.append(src)
    for x_,y_ in point_lst:
        x,y = last
        dir_,x_,y_ = direction(x,y,x_,y_)
        directions.append(dir_)
        dis_ = distance(x,y,x_,y_)
        dist += dis_
        last = x_,y_
        new_point_lst.append(last)
    line_lst.append(new_point_lst)
    return src_pt,dest_pt,dist,directions

def gui():
    pygame.init()
    mark_lst = []
    line_lst = []
    relation_lst = []
    point_lst = []
    screen = pygame.display.set_mode((1252,582),0,32)
    background = pygame.image.load('map.png').convert()
    mark_ = mark()
    fout = open('coord.txt','w')
    while True:
        for event in pygame.event.get():
            #event
            if event.type == QUIT:         #quit
                print 'exit'
                exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_q:       #quit
                    print 'exit'
                    exit(0)
                elif event.mod&KMOD_CTRL and event.key==K_m:
                    print 'undo mark list'
                    mark_lst.pop()
                elif event.mod&KMOD_CTRL and event.key==K_l:
                    print 'undo line list'
                    line_lst.pop()
                elif event.mod&KMOD_CTRL and event.key==K_i:
                    print 'undo relation list'
                    relation_lst.pop()
                elif event.mod&KMOD_CTRL and event.key==K_s:
                    print 'save'
                    if len(relation_lst) == 0:
                        fout = open('coord.txt','w')
                        for x,y,pt,m in mark_lst:
                            fout.write('%s\t%d %d\n'%(pt,x,y))
                        fout.close()
                    else:
                        fout = open('relation.txt','w')
                        for src_pt,dest_pt,dist,directions in relation_lst:
                            fout.write('%s\t%s\t%d\t%s\n'%(src_pt,dest_pt,dist,' '.join(directions)))
                        fout.close()
                elif event.key == K_RETURN:
                    #src,dest,dist,directions = relation_info(point_lst)
                    src_pt,dest_pt,dist,directions = relation_info(point_lst,mark_lst,line_lst)
                    print src_pt,dest_pt,dist,directions
                    relation_lst.append((src_pt,dest_pt,dist,directions))
                    point_lst = []
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:      #new point
                    x = event.pos[0]
                    y = event.pos[1]
                    dialog = input_dialog(x,y)
                    dialog.show()
                    pt,x,y = dialog.get()
                    if not pt == None:
                        mark_lst.append((x,y,pt,mark_.getone()))
                        print 'add ',pt,x,y
                elif event.button == 3:      #dist
                    x = event.pos[0]
                    y = event.pos[1]
                    point_lst.append((x,y))
                    #print 'line'
        screen.blit(background,(0,0))
        for x,y,pt,m in mark_lst:
            screen.blit(m,(x-15,y-15))
        for pt_lst in line_lst:
            pygame.draw.lines(screen,(0,255,0),False,pt_lst,3)
        for x,y in point_lst:
            pygame.draw.circle(screen,(0,0,255),(x,y),10)
        pygame.display.update()

if __name__=='__main__':
    gui()
