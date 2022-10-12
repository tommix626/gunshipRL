# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 00:10:07 2021

@author: Tom
"""

# cartpole文件在   环境文件夹\Lib\site-packages\gym\envs\classic_control
# gym安装：pip install gym matplotlib -i  https://pypi.tuna.tsinghua.edu.cn/simple
import random
import torch
import torch.nn as nn
import numpy as np
from gunship_env_v1 import *

feature_num,action_num=40,4

class MyNet(nn.Module):
    def __init__(self):
        super(MyNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(feature_num, 24),
            nn.ReLU(),
            nn.Linear(24, 24),
            nn.ReLU(),
            nn.Linear(24, action_num)
        )
        self.mls = nn.MSELoss()
        self.opt = torch.optim.Adam(self.parameters(), lr = 0.001)

    def forward(self, inputs):
        return self.fc(inputs)




net = MyNet()
net2 = MyNet()

store_count = 0
store_size = 20000  # buffer size
decline = 0.6  # 衰减系数
learn_time = 0
update_time = 20
gama = 0.9
b_size = 2000  # batch size
store = np.zeros((store_size, 8))  # 初始化buffer 列中储存 s, a, s_, r =2+3+2+1
start_study = False
'''
for i in range(50000):
    fwork.reset()#fwork.reset() 按下R键 
    s = fwork.feature_collect(self)
    while True:
        if random.randint(0,100) < 100*(decline**learn_time):
            a = random.randint(0,action_num)
        else:
            out = net(torch.Tensor(s)).detach()  # out中是四种操作认为的expected future return
            a = torch.argmax(out).data.item()
        s_, r, done = fwork.play(action=a,re=1) #  re=1 有返回值
        #storing
        store[store_count % store_size][0:feature_num] = s
        store[store_count % store_size][feature_num:feature_num+action_num] = a
        store[store_count % store_size][feature_num+action_num:2*feature_num+action_num] = s_
        store[store_count % store_size][2*feature_num+action_num:2*feature_num+action_num+1] = r
        store_count += 1
        s = s_
        if(store_count%100==0):
            print(store_count)

        if store_count > store_size:

            if learn_time % update_time == 0:
                net2.load_state_dict(net.state_dict()) #net para -> net2

            index = random.randint(0, store_size - b_size -1)#SGD
            b_s  = torch.Tensor(store[index:index + b_size, 0:feature_num])
            b_a  = torch.Tensor(store[index:index + b_size, feature_num:feature_num+action_num]).long()
            b_s_ = torch.Tensor(store[index:index + b_size, feature_num+action_num:2*feature_num+action_num])
            b_r  = torch.Tensor(store[index:index + b_size, 2*feature_num+action_num:2*feature_num+action_num+1])

            q = net(b_s).gather(1, b_a)#input b_s(minibatch) output中抽取第一维度上的action
            q_next = net2(b_s_).detach().max(1)[0].reshape(b_size, 1)
            tq = b_r + gama * q_next
            loss = net.mls(q, tq)
            net.opt.zero_grad()
            loss.backward()
            net.opt.step()

            learn_time += 1
            if not start_study:
                print('start study')
                start_study = True
                break
        if done:
            break
'''