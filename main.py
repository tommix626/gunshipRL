# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 19:19:01 2021

neg h stone
x-side detector
put writer in fwork
@author: Tom
"""
import pygame,sys,random
from gunship_env_v1 import *
#from AI_agent import *
#from AI_agent_randomY import *
from AI_agent_normal import *
#from torch_v1 import *
# from tensorboardX import SummaryWriter
#***************************************************
SCREEN_W, SCREEN_H = 1000, 600
SPACE_UP, SPACE_DOWN = 110,540
SPEEDY_MAX = 3
BG_COLOR, BORDER_COLOR = (0, 0, 80), (80, 80, 80)
G = 0.5
#***************************************************
writer = None # writer = SummaryWriter("temp/greedy")


    





#***************************************************
pygame.init()
screen = pygame.display.set_mode(( SCREEN_W, SCREEN_H))
pygame.display.set_caption('GUNSHIP')
clock = pygame.time.Clock()

fwork = CLS_framework(screen,writer=writer)
air = CLS_AI_Agent(fwork,fnum=44,anum=4)
fwork.airList.append(air)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            fwork.keydown(event.key)
        if event.type == pygame.KEYUP:
            fwork.keyup(event.key)
    fwork.run()
    

writer.close()