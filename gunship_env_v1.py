import pygame, sys, random, math, torch
import numpy as np
SCREEN_W, SCREEN_H = 1000, 600
SPACE_UP, SPACE_DOWN = 110,540
SPEEDY_MAX = 3
BG_COLOR, BORDER_COLOR = (0, 0, 80), (80, 80, 80)
G = 0.5
AngList=[i/5 for i in range(-9,10)]
def collide(x1,y1,w1,h1,x2,y2,w2,h2):
    if x1 + w1 > x2 and x1 < x2 + w2 and y1 + h1 > y2 and y1 < y2 + h2:
        return True
    return False

class CLS_gunship( object ):
    def __init__( self, pic, x, y, w, h, interval, frameNum ):
        self.pic = pic
        self.x, self.y, self.w, self.h = x, y, w, h
        self.interval, self.frameNum = interval, frameNum
        self.counter = 0
        self.speedY, self.accY = 0, 0
        self.state = 0
        self.score = 0
        self.bulletList = []
        self.bltCD=50
        self.bltcd=self.bltCD

    def move( self ):
        #self.speedY += (self.accY + G)
        if self.speedY < -SPEEDY_MAX:
            self.speedY = -SPEEDY_MAX
        elif self.speedY > SPEEDY_MAX:
            self.speedY = SPEEDY_MAX
        self.y += self.speedY
        if self.y < SPACE_UP:
            self.y = SPACE_UP
        elif self.y > SPACE_DOWN - self.h:
            self.y = SPACE_DOWN - self.h
        if(self.bltcd>0):
            self.bltcd-=1
    def draw( self, scr ):
        currentNum = (self.counter // self.interval) % self.frameNum
        self.counter += 1
        if self.state == 1:
            currentNum = 4
        scr.blit( self.pic, ( self.x, self.y ),( 0, currentNum * self.h, self.w, self.h ))
        
#**********************************************************************
STONE_H_MIN,STONE_H_MAX,STONE_W = 50,200,30
STONE_SPACE = 150
STONE_SPEED,STONE_START_X = 3,1000
#**************************************************************************
class CLS_stone( object ):
    def __init__( self ):
        self.x,self.w = STONE_START_X,STONE_W
        h = random.randint(STONE_H_MIN,STONE_H_MAX)
        self.h = h
        if h % 2 == 0:
            self.y = SPACE_UP
        else:
            self.y = SPACE_DOWN - h
    def move(self):
        self.x -= STONE_SPEED
    def draw(self,scr):
        pygame.draw.rect( scr,(random.randint(1,200),0,200),\
                          (self.x ,self.y,self.w,self.h),0)
class CLS_framework(object):
    def __init__(self,screen,writer=None):
        self.scr = screen
        self.clock = pygame.time.Clock()
        self.state = 0
        self.font = pygame.font.Font(None,32)
        self.airList = []
        self.stoneList = []
        self.lastStoneX = 0
        self.face = pygame.image.load('face.bmp')
        self.dotList=[]
        self.writer=writer
        self.cntaction=[0]*4

    def run(self):
        self.airList[0].train()
        #self.airList[0].train_n(3)
    def play( self ,action=-1,re=0,ranY=0):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if self.state == 1:
            return
        air=self.airList[0]
        #初始环境
        s_init = self.feature_collect(air)
        reward = 0
        #施加动作
        if(action != -1):
            if(action==2 or action==3):#shoot
                if(self.airList[0].bltcd<=0):#CD-OK
                    bullet = CLS_bullet( self.airList[0].x + 84,self.airList[0].y + 15,random.random()*3+1)
                    self.airList[0].bulletList.append(bullet)
                    self.airList[0].bltcd=self.airList[0].bltCD
            if(action==1 or action==3):#fly
                self.airList[0].speedY = -3
            else:
                self.airList[0].speedY = 3
            self.cntaction[action]+=1
        #获得新环境（并渲染）
        self.scr.fill( (0,0,0) )
        self.draw( )#画背景
        #探测器绘图
        #print("dtList_len=",len(self.dotList))
        for pair in self.dotList:
            c=255-max(min([150,pair[2]//3]),0)
            #print("c=",c)
            pygame.draw.line(self.scr,(c,305-c,50),pair[0],pair[1],3)
        for stone in self.stoneList:#对于每一块石头：
            #移动、绘图和删除
            stone.move()
            stone.draw( self.scr )
            self.lastStoneX = stone.x
            if stone.x + stone.w < 0:
                self.stoneList.pop( 0 )
            #与直升机死亡判定与出界加分判断
            for air in self.airList:
                if (air.x + air.w >= stone.x and air.x <=stone.x + stone.w):#纵坐标有重合部分（余下剪枝）
                    if (air.y + air.h >= stone.y and air.y <=stone.y + stone.h):
                        air.state = 1
                        self.state = 1
                    else:
                        air.score += stone.h//100
                        reward +=stone.h+100
        #新石头的生成
        if STONE_START_X - self.lastStoneX \
           > random.randint(STONE_SPACE,STONE_SPACE+ \
                            STONE_SPACE // 2):
            stone = CLS_stone()
            self.stoneList.append( stone)
        #直升机的移动、显示和子弹操作
        for air in self.airList:
            air.move()
            air.draw(self.scr)
            i = 0
            while i < len(air.bulletList):#子弹：
                b = air.bulletList[i]
                #子弹的删除
                if not b.move():#如果返回false 直接删除
                    air.bulletList.pop(i)
                    continue
                #子弹撞上石头
                for s in self.stoneList:
                    if collide(b.x,b.y,b.w,b.h,s.x,s.y,s.w,s.h):
                        air.bulletList.pop(i)
                        s.h -= 20
                        reward+=5
                        air.score += 20
                        if s.h % 2 == 1:
                            s.y += 20
                #子弹的绘图
                b.draw(self.scr)
                i += 1
        s_ = self.feature_collect(air)
        
        pygame.display.update()
        clock.tick(300)
        #返回
        if(re and ranY):
            if self.state == 1:
                return s_, -1000, 1, s_init
            return s_, reward, 0, s_init
        if(re==1 and ranY==0):
            if self.state == 1:
                return s_, -1000, 1
            return s_, reward, 0
    def draw( self ):   #绘制背景
        pygame.draw.rect(self.scr,BG_COLOR,(0,SPACE_UP, SCREEN_W, SPACE_DOWN - SPACE_UP),0)
        pygame.draw.rect(self.scr,BORDER_COLOR,(0, SPACE_DOWN,SCREEN_W, 10),0)
        pygame.draw.rect(self.scr,BORDER_COLOR,(0, SPACE_UP - 10,SCREEN_W, 10),0)
        img = self.font.render('SCORE:' + \
                               str(self.airList[0].score),True,(160,180,0))
        self.scr.blit(img,(SCREEN_W - 200,10))
        self.scr.blit(self.face,(100,0))
    def keydown(self,key):
        if key == pygame.K_UP:
            self.airList[0].accY = -1
        if key == pygame.K_r:
            self.reset()
        if key == pygame.K_SPACE:
            if(self.airList[0].bltcd>0):#CD-ing
                return
            bullet = CLS_bullet( self.airList[0].x + 84,self.airList[0].y + 15,random.random()*3+1)
            self.airList[0].bulletList.append(bullet)
            self.airList[0].bltcd=self.airList[0].bltCD
        return
    def keyup(self,key):
        if key == pygame.K_UP:
            self.airList[0].accY = 0
    def feature_collect(self,air):
        s=[]
        #air *3
        s.append(air.y+air.h//2) #air y(center)
        s.append(air.speedY) # air spdY
        s.append(air.accY) 
        #last stone *5
        if(len(self.stoneList)>0):
            ls = self.stoneList[0]
            s.append(ls.x-air.x-air.w) #dis FIXME why neg exist?
            s.append(ls.h)#height
            uplim,downlim=air.y-ls.y-ls.h,ls.y-air.y+air.h
            posf = uplim*downlim
            s.append(uplim)
            s.append(downlim)
            s.append(posf)
        else:
            s.append(1000)
            s.append(0)
            s.append(0)
            s.append(0)
            s.append(0)
        #length of line *19 + detected stone *3
        dist=[0]*19
        flagg=1
        for i in range(len(self.dotList)):
            self.dotList.pop( 0 )
        self.dotlist=[]
        x0,y0=air.x+air.w,air.y+air.h//2
        for stone in self.stoneList:
            x,y,h=stone.x,stone.y,stone.h
            if(x-x0 <= 0):#valid stone
                continue
            for i in range(19):
                ang=AngList[i]
                ty = y0-(x-x0)*math.tan(ang)
                if(ty>=y and ty<=y+h and dist[i]==0):
                    dist[i]=(x-x0)/math.cos(ang)
                    self.dotList.append([(x0,y0),(x,ty),dist[i]])
                    if(ang==0):
                        flagg=0
                        ls = stone
                        s.append(ls.x-air.x-air.w) #dis FIXME why neg exist?
                        s.append(ls.h)#height
                        uplim,downlim=air.y-ls.y-ls.h,ls.y-air.y+air.h
                        s.append(uplim)
                        s.append(downlim)
        if(flagg):
            s.append(1000)
            s.append(0)
            s.append(0)
            s.append(0)
        for ele in dist:
            if(ele==0):
                s.append(1/0.001)
            else:
                s.append(1/ele)
        #bullet *13=1+3*4
        s.append(air.bltcd)
        cnt=0
        for blt in air.bulletList:
            if(cnt>=3):
                break
            x,y,spdX=blt.x+blt.w,blt.y+blt.h//2,blt.speedX
            s.append(1)
            s.append(x)
            s.append(y)
            s.append(spdX)
            cnt+=1;
        for i in range(cnt,3):
            s.append(0)
            s.append(0)
            s.append(0)
            s.append(0)
        #print("s=",s)
        #print("s_len=",len(s))
        return torch.Tensor(s)
    def reset(self):
        self.state,self.lastStoneX = 0,0
        for air in self.airList:
            air.state,air.score = 0,0
            air.y=SCREEN_H//2
        self.stoneList = []
        return
    def ranY(self,flag=0):
        if(random.random()>0.99 or flag):
            for air in self.airList:
                a = np.random.normal(loc=0,scale=1)*70
                air.y=(SPACE_UP+SPACE_DOWN)//2-air.h//2+a
        

class CLS_bullet(object):
    def __init__( self,x,y,speedX ):
        self.pic = pygame.image.load('bullet.bmp')
        self.pic.set_colorkey( (0,0,0) )
        self.x,self.y = x,y
        self.w,self.h = self.pic.get_size()
        self.speedX = speedX
    def move(self):
        self.x += self.speedX
        if self.x > SCREEN_W:
            return False
        return True
    def draw (self,scr):
        scr.blit(self.pic,(self.x,self.y))


pygame.init()
clock = pygame.time.Clock()      

        






        
