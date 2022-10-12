# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 18:40:19 2021

@author: Tom
"""

from gunship_env_v1 import *
import pygame
import random
import torch
import torch.nn as nn
import numpy as np




class CLS_AI_Agent(CLS_gunship):
    def __init__(self,fwork,fnum=44,anum=4):
        self.fnum,self.anum=fnum,anum
        actPic = pygame.image.load('gunship.bmp')
        actPic.set_colorkey((0, 0, 0))
        super().__init__(actPic, 40, 100, 84, 30, 3, 4)
        self.net = MyNet()
        self.net2 = MyNet()
        self.fwork = fwork
        self.store_count = 0
        self.store_size = 30000  # buffer size
        self.store = np.zeros((self.store_size, 2*fnum+anum+1))  # 初始化buffer 列中储存 s, a, s_, r =2*feature_num+action_num+1
        self.start_study = False
        self.writer = fwork.writer
        self.learn_time=0
        return
    def take_action(self,s):
        return
    def train(self,times=1):
        self.store_count
        store_size=self.store_size
        self.start_study
        store=self.store
        net=self.net
        net2=self.net2
        decline = 30000  # 衰减系数
        update_time = 20000
        gama = 0.9
        b_size = 1500  # batch sizes
        feature_num,action_num=self.fnum,self.anum
        for t in range(times):
            self.fwork.reset()#fwork.reset() 按下R键 
            for skip in range(250):
                self.fwork.play()
            s = self.fwork.feature_collect(self.fwork.airList[0])
            #print("s=",s)
            while True:
                s=self.fwork.feature_collect(self.fwork.airList[0])
                epilson=min([1,self.learn_time/decline])
                if random.random() < 1.1-epilson:
                    a = random.randint(0,action_num-1)
                else:
                    out = net(torch.Tensor(s)).detach()  # out中是四种操作认为的expected future return
                    a = torch.argmax(out).data.item()
                s_, r, done = self.fwork.play(action=a,re=1) #  re=1 有返回值
                #print("s=",s)
                #storing
                store[self.store_count % store_size][0:feature_num] = s
                store[self.store_count % store_size][feature_num:feature_num+action_num] = a
                store[self.store_count % store_size][feature_num+action_num:2*feature_num+action_num] = s_
                store[self.store_count % store_size][2*feature_num+action_num:2*feature_num+action_num+1] = r
                self.store_count += 1
                s = s_
                if(self.store_count%100==0):
                    print(self.store_count)
                    print("epilson=",epilson)
                    print(self.fwork.cntaction)
        
                if self.store_count > store_size:
                    self.learn_time += 1
                    if self.learn_time % update_time == 0:
                        net2.load_state_dict(net.state_dict()) #net para -> net2
        
                    index = random.randint(0, store_size - b_size -1)#SGD
                    b_s  = torch.Tensor(store[index:index + b_size, 0:feature_num])
                    b_a  = torch.Tensor(store[index:index + b_size, feature_num:feature_num+action_num]).long()
                    b_s_ = torch.Tensor(store[index:index + b_size, feature_num+action_num:2*feature_num+action_num])
                    b_r  = torch.Tensor(store[index:index + b_size, 2*feature_num+action_num:2*feature_num+action_num+1])
        
                    #print(b_a)
                    q = net(b_s).gather(1, b_a)#input b_s(minibatch) output中抽取第一维度上的action
                    q_next = net2(b_s_).detach().max(1)[0].reshape(b_size, 1)
                    tq = b_r + gama * q_next
                    loss = net.mls(q, tq)
                    #print(loss,self.learn_time)
                    #self.writer.add_scalar("Loss",loss,self.learn_time)
                    net.opt.zero_grad()
                    loss.backward()
                    net.opt.step()
        
                    
                    if not self.start_study:
                        print('start study')
                        self.start_study = True
                        break
                if done:
                    #print(score)
                    #self.writer.add_scalar("Game Score",self.score,self.store_count)
                    break


class MyNet(nn.Module):
    def __init__(self,fn=44,an=4):
        feature_num,action_num=fn,an
        super(MyNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(feature_num, 100),
            nn.Tanh(),
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, action_num)
        )
        self.mls = nn.MSELoss()
        self.opt = torch.optim.Adam(self.parameters(), lr = 0.000001)

    def forward(self, inputs):
        return self.fc(inputs)
