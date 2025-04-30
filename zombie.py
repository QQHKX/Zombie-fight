# coding:utf-8
import pygame, sys, time, random
from pygame.locals import*
# 初始化pygame环境
pygame.init()
# 设置一个长为1250，宽为700的窗口
canvas = pygame.display.set_mode((1200, 600))
canvas.fill([255, 255, 255])
# 设置窗口标题
pygame.display.set_caption("炮打僵尸_无尽版")
#背景音乐加载
pygame.mixer.music.load("img/Laura Shigihara - Zombies On Your Lawn.mp3")
pygame.mixer.music.play()
# 背景图片加载
bg = pygame.image.load('img/background.jpg')
bg1 = pygame.image.load('img/game_over_screen.png')
bg_end = pygame.image.load('img/game_over_screen.png')
# 加载大炮等图片
wq = pygame.image.load('img/cannon.png')
zd = pygame.image.load('img/bullet.png')
# 僵尸的三种状态
# ：移动、攻击、站立
MOVE = 0
STAND = 1
ATTACK = 2
#退出游戏控量
win=0
# 将所有动画帧图片对象存储到列表中
# 僵尸移动图片数组
zombieM = []
for i in range(1, 14):
    if i < 10:
        zombieM.append(pygame.image.load('img/move/0' + str(i) + '.png'))
    else:
        zombieM.append(pygame.image.load('img/move/' + str(i) + '.png'))

def fillText(text, position):
    # 设置字体样式和大小
    my_font = pygame.font.Font("img/fonts/regular.ttf", 50)
    # 渲染文字
    text = my_font.render(text, True, (0, 0, 0))
    canvas.blit(text, position)
def fillText2(text, position):
    # 设置字体样式和大小
    my_font = pygame.font.Font("img/fonts/warning.ttf", 80)
    # 渲染文字
    text = my_font.render(text, True, (255, 0, 0))
    canvas.blit(text, position)
def fillText3(text, position):
    # 设置字体样式和大小
    my_font = pygame.font.Font("img/fonts/regular.ttf", 50)
    # 渲染文字
    text = my_font.render(text, True, (0, 255, 255))
    canvas.blit(text, position)
def fillText4(text, position):
    # 设置字体样式和大小
    my_font = pygame.font.Font("img/fonts/game_over.ttf", 100)
    # 渲染文字
    text = my_font.render(text, True, (255, 12, 3))
    canvas.blit(text, position)
# 僵尸的状态：移动
MOVE = 0
# 创建列表存储子弹对象
bullet_list = []
def handleEvent():
    global bullet_list
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        # 鼠标事件
        if event.type == MOUSEMOTION:
                Game.player.y = event.pos[1] - Game.player.height / 2

        # 每次点击鼠标就创建一个子弹对象储存到子弹列表中
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and len(bullet_list)<=isTime2():
            bullet_list.append(Zd(Game.player.width, event.pos[1] - 20))
# 定义子弹类
class Zd():
    def __init__(self, x, y):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.tp = zd
        self.sd = isTime2()+1
        self.sj = time.time()
        self.cd = False
    # 创建子弹碰撞检测
    def checkHit(self,zom):
        if self.x-80 >=zom.x and (self.y-20 >= zom.y and self.y <=zom.y+180):
            return 1
    # 画子弹方法
    def paint(self):
        canvas.blit(self.tp, (self.x, self.y))

    # 子弹移动方法
    def move(self):
        canvas.blit(self.tp, (self.x, self.y))
        self.x += self.sd-2
# 定义僵尸类
class Zombie():
    def __init__(self, y, speed):
        self.speed = speed
        self.x = 1200
        self.y = y
        self.width = 180
        self.height = 180
        self.state = MOVE
        self.index = 0
        self.frame = zombieM[self.index]


    #创建画僵尸和僵尸移动方法
    def paint(self):
        canvas.blit(self.frame, (self.x, self.y))

    def move(self):
        self.x -= self.speed

    #僵尸播放动画方法
    def animation(self):
        if self.state == MOVE:
            self.frame = zombieM[self.index % 13]
            self.move()
        elif self.state == STAND:
            self.frame = zombieS[self.index % 6]
        elif self.state == ATTACK:
            self.frame = zombieA[self.index % 11]
        self.index += 1
class Player():
    def __init__(self, x, y, img):
        self.width = 64
        self.height = 64
        self.x = x
        self.y = y
        self.rx = x
        self.ry = y
        self.img = wq
        self.xl = 3
        self.score = 0

    # 画大炮(玩家)方法
    def paint(self):
        canvas.blit(self.img, (self.x, self.y))

class Game:
    player = Player(0, 0, wq)
# 创建列表存储僵尸对象
zombie_list = []
# 创建僵尸时间间隔方法
startTime = time.time()
def isTime():
    global startTime
    currentTime = time.time()
    if currentTime - startTime >=2:
        startTime = time.time()
        return 1
# 创建子弹生成时间间隔方法
startTime2 = time.time()
def isTime2():
    global startTime2
    currentTime2 = time.time()
    return int(currentTime2 - startTime2+2)
# 创建僵尸对象生成方法
def createZombies():
    for i in range(0,int(isTime2()/5)+5):
        y = random.randint(0,420)
        speed = random.randint(int(isTime2()/3)+1,int(isTime2()/3)+2)
        zombie_list.append(Zombie(y,speed))

# 僵尸胜利方法
def zombiewin():
    global win
    for zombi in zombie_list:
        if zombi.x <= 0:
            pygame.mixer.music.stop()
            canvas.blit(bg, (0, 0))
            canvas.blit(bg_end, (0, 0))
            fillText4('游戏结束！',(200,200))
            win+=1


# 创建僵尸、子弹删除方法
def delete():
    for bul in bullet_list:
        bul.paint()
        bul.move()
        for zom in zombie_list:
            if bul.checkHit(zom):
                bullet_list.remove(bul)
                zombie_list.remove(zom)
                Game.player.score += 1
                break

if __name__ == '__main__':
    while True:
        if win<10:
            #画出背景、僵尸移动
            canvas.blit(bg, (0, 0))
            Game.player.paint()
            delete()
            if Game.player.score>=210 and Game.player.score<=250:
                fillText2('(阶段2)觉得自己很帅？僵尸不这么想！！！，感受恐惧吧！！',(200,100))
            if Game.player.score>=0 and Game.player.score<=10:
                fillText3('(阶段1)随着时间的推移 你会变强，但僵尸也会！',(270,100))
            if isTime():
                createZombies()
            for zom in zombie_list:
                zom.paint()
                zom.animation()
            zombiewin()
            fillText('SCORE：' + str(Game.player.score), (900, 10))
            time.sleep(0.007)
        pygame.display.update()
        handleEvent()
