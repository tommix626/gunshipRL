import pygame, sys, random
SCREEN_W, SCREEN_H = 1000, 600
SPACE_UP, SPACE_DOWN = 110,540
SPEEDY_MAX = 3
BG_COLOR, BORDER_COLOR = (0, 0, 80), (80, 80, 80)
G = 0.5
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
        self.soundBullet = pygame.mixer.Sound('bullet.wav')

    def move( self ):
        self.speedY += (self.accY + G)
        if self.speedY < -SPEEDY_MAX:
            self.speedY = -SPEEDY_MAX
        elif self.speedY > SPEEDY_MAX:
            self.speedY = SPEEDY_MAX
        self.y += self.speedY
        if self.y < SPACE_UP:
            self.y = SPACE_UP
        elif self.y > SPACE_DOWN - self.h:
            self.y = SPACE_DOWN - self.h
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
        self.speedY = 0
    def move(self):
        self.x -= STONE_SPEED
        self.y += self.speedY
        if self.y < SPACE_UP:
            self.y = SPACE_UP
            self.speedY = -self.speedY
        if self.y > SPACE_DOWN - self.h:
            self.y = SPACE_DOWN - self.h
            self.speedY = -self.speedY
    def draw(self,scr):
        pygame.draw.rect( scr,(random.randint(1,200),0,200),\
                          (self.x ,self.y,self.w,self.h),0)
class CLS_framework(object):
    def __init__(self,screen):
        self.scr = screen
        self.clock = pygame.time.Clock()
        self.state = 0
        self.font = pygame.font.Font(None,32)
        self.z10List = []
        self.stoneList = []
        self.lastStoneX = 0
        self.face = pygame.image.load('face.bmp')
        self.bangList = []

    def play( self ):
        if self.state == 1:
            return
        self.scr.fill( (0,0,0) )
        self.draw( )
        for stone in self.stoneList:
            if random.random() < 0.01:
                stone.speedY = random.randint(-2,2)
            stone.move()
            stone.draw( self.scr )
            self.lastStoneX = stone.x
            if stone.x + stone.w < 0:
                self.stoneList.pop( 0 )
            for z10 in self.z10List:
                if (z10.x + z10.w >= stone.x and\
                    z10.x <=stone.x + stone.w):
                    if (z10.y + z10.h >= stone.y and\
                    z10.y <=stone.y + stone.h):
                        z10.state = 1
                        self.state = 1
                        soundDie.play()
                    else:
                        z10.score += abs(stone.h//100)
        if STONE_START_X - self.lastStoneX \
           > random.randint(STONE_SPACE,STONE_SPACE+ \
                            STONE_SPACE // 2):
            stone = CLS_stone()
            self.stoneList.append( stone)
        for z10 in self.z10List:
            z10.move()
            z10.draw(self.scr)
            i = 0
            while i < len(z10.bulletList):
                b = z10.bulletList[i]
                if not b.move():
                    z10.bulletList.pop(i)
                    continue
                for s in self.stoneList:
                    if collide(b.x,b.y,b.w,b.h,s.x,s.y,s.w,s.h):#函数见开头，判断stone与bullet是否碰撞
                        z10.bulletList.pop(i)#把碰撞的bullet去掉
                        s.h -= 20#bullet效果：stone缩短
                        if s.h % 2 == 1:#与上面：h为奇数stone从顶上往下长呼应，达到使stone往上缩的目的
                            s.y += 20
                        if s.h % 5 == 0:#机率触发*
                            if s.speedY>=0.5:
                                s.speedY-=0.5
                            elif s.speedY<=-0.5:
                                s.speedY+=0.5
                            

                b.draw(self.scr)
                i += 1
            
        pygame.display.update()
        clock.tick(100)
    def draw( self ):   
        pygame.draw.rect(self.scr,BG_COLOR,(0,SPACE_UP, SCREEN_W, SPACE_DOWN - SPACE_UP),0)
        pygame.draw.rect(self.scr,BORDER_COLOR,(0, SPACE_DOWN,SCREEN_W, 10),0)
        pygame.draw.rect(self.scr,BORDER_COLOR,(0, SPACE_UP - 10,SCREEN_W, 10),0)
        img = self.font.render('SCORE:' + \
                               str(self.z10List[0].score),True,(160,180,0))
        self.scr.blit(img,(SCREEN_W - 200,10))
        self.scr.blit(self.face,(100,0))
    def keydown(self,key):
        if event.key == pygame.K_UP:
            self.z10List[0].accY = -1
        if event.key == pygame.K_r:
            self.state,self.lastStoneX = 0,0
            for z10 in self.z10List:
                z10.state,z10.score = 0,0
            self.stoneList = []
            self.z10List[0].bulletList = []
        if event.key == pygame.K_SPACE:
            for i in range (3):
                bullet = CLS_bullet( self.z10List[0].x + 84,self.z10List[0].y,10,1*(i-1),0.5)
                self.z10List[0].bulletList.append(bullet)
                self.z10List[0].soundBullet.play()
            


            
    def keyup(self,key):
        if event.key == pygame.K_UP:
            self.z10List[0].accY = 0

class CLS_bullet(object):
    def __init__( self,x,y,speedX,speedY,accX ):
        self.pic = pygame.image.load('bullet.bmp')
        self.pic.set_colorkey( (0,0,0) )
        self.x,self.y = x,y
        self.w,self.h = self.pic.get_size()
        self.speedX = speedX
        self.speedY = speedY
        self.timer=50
        self.accX=accX
    def move(self):
        while self.timer>0:
            self.timer-=1
            self.x+=self.accX
            self.y+=self.speedY
            return True
        self.x += self.speedX
        if self.x > SCREEN_W:
            return False
        return True
    def draw (self,scr):
        scr.blit(self.pic,(self.x,self.y))

class CLS_bang(object):
    def __init__(self,x,y,timer):
        self.pic = pygame.image.load('bang40.bmp')
        self.pic.set_colorkey( (0,0,0) )
        self.x,self.y = x,y
        self.w,self.h = self.pic.get_size()
        self.timer = timer
    def move(self):
        self.x -= STONE_SPEED
        self.timer -= 1
    def draw(self,scr):
        scr.blit(self.pic,(self.x - self.w//2,self.y - self.h//2))
        

        
pygame.init()
screen = pygame.display.set_mode(( SCREEN_W, SCREEN_H))
pygame.display.set_caption('GUNSHIP')
clock = pygame.time.Clock()
actPic = pygame.image.load('gunship.bmp')
actPic.set_colorkey((0, 0, 0))
z10 = CLS_gunship( actPic, 40, 100, 84, 30, 3, 4)
fwork = CLS_framework(screen)
fwork.z10List.append(z10)
soundDie = pygame.mixer.Sound('mariodie.wav')
soundShoot = pygame.mixer.Sound('bullet.wav')
pygame.mixer.music.load('bg1.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=0)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            fwork.keydown(event.key)
        if event.type == pygame.KEYUP:
            fwork.keyup(event.key)
    fwork.play()
'''
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen,BG_COLOR,(0,SPACE_UP, SCREEN_W, SPACE_DOWN - SPACE_UP),0)
    pygame.draw.rect(screen,BORDER_COLOR,(0, SPACE_DOWN,SCREEN_W, 10),0)
    pygame.draw.rect(screen,BORDER_COLOR,(0, SPACE_UP - 10,SCREEN_W, 10),0)

    for stone in stoneList:
        stone.move()
        stone.draw( screen )
        lastStoneX = stone.x
        if stone.x + stone.w < 0:
            stoneList.pop( 0 )
        #crash
    if STONE_START_X - lastStoneX > \
       random.randint(STONE_SPACE,STONE_SPACE+STONE_SPACE//2):
        stone = CLS_stone( )
        stoneList.append( stone )
    z10.move()
    z10.draw(screen)
    pygame.display.update()
    clock.tick(100)

            
'''


        






        
