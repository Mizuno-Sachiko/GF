import pygame
import os
import random
import math
import time

# 初始化 Pygame
pygame.init()

# 设置窗口大小和标题
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("终焉花海")


# 设置时钟控制帧率
clock = pygame.time.Clock()
fps = 60  # 每秒播放的帧数


#加载完文件根目录设定
root_folder=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

icon = pygame.image.load(f"{root_folder}/GF/icon/icon.png")
pygame.display.set_icon(icon)

#音效初始化
pygame.mixer.init()
shot=pygame.mixer.Sound(f"{root_folder}/GF/Sound/gun.wav")
bgmusic_combat=pygame.mixer.music.load(f"{root_folder}/GF/Sound/M_19summer_song.wav") #战斗
bgmusic_main=pygame.mixer.music.load(f"{root_folder}/GF/Sound/M_19summer_zombie_h.ogg") #页面
music_load_count=0 #播放标题后为1 播放战斗为2

#页面变量
Game_START=False
WIN=False
LOSE=False
Game_LOAD=False
AGAIN=False


#定义加载动画函数
def load_Anime_png(folder_path, num):
    Anime = []
    for i in range(num):
        image_path = os.path.join(folder_path, f"{i}.png")
        image = pygame.image.load(image_path).convert_alpha()
        Anime.append(image)
    return Anime

#定义加载动画函数
def load_Anime_jpg(folder_path, num):
    Anime = []
    for i in range(num):
        image_path = os.path.join(folder_path, f"{i}.jpg")
        image = pygame.image.load(image_path).convert_alpha()
        Anime.append(image)
    return Anime

#加载动画
M4A1_wait = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_wait", 54)#数目均为张数+1
M4A1_move = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_move", 24)
M4A1_attack = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_attack", 34)
M4A1_backattack = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_backattack", 34)
M4A1_back = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_back", 31)
M4A1_moveattack = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_moveattack", 24)
M4A1_die = load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_die", 137)
M4A1_skill= load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_skill", 59)
M4A1_spmove= load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_spmove", 48)
M4A1_backskill= load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_backskill", 62)
M4A1_win= load_Anime_png(f"{root_folder}/GF/M4A1/M4A1_win", 142)

nyto_attack1 = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_attack1", 50)
nyto_attack2 = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_attack2", 67)
nyto_die = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_die", 167)
nyto_skill3 = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_skill3", 67)
nyto_skill4 = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_skill4", 639)
nyto_move = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_move", 40)
nyto_wait = load_Anime_png(f"{root_folder}/GF/Nyto/nyto_wait", 54)
phantom_dash = load_Anime_png(f"{root_folder}/GF/phantom/phantom_dash", 140)
load_pic_list = load_Anime_jpg(f"{root_folder}/GF/art/Load", 395)
load_pic_num = 0

#
M4A1_pic=pygame.image.load(f"{root_folder}/GF/art/pic_m4a1mod 720.png").convert_alpha()
background = pygame.image.load(f"{root_folder}/GF/BG/2019summer_5 720.png").convert_alpha()
wait_background=pygame.image.load(f"{root_folder}/GF/BG/2019summer_10 720.png").convert_alpha()
wait_background_logo=pygame.image.load(f"{root_folder}/GF/art/logo.png").convert_alpha()
subtitle=pygame.image.load(f"{root_folder}/GF/art/subtitle.png").convert_alpha()
description=pygame.image.load(f"{root_folder}/GF/art/description.png").convert_alpha()
Win_pic=pygame.image.load(f"{root_folder}/GF/BG/Shattered_Connexion_Login_Wallpaper2 720.png").convert_alpha()  #pygame.image.load(f"{root_folder}/GF/BG/Shattered_Connexion_Login_Wallpaper2 720.png").convert_alpha()
Win_description=pygame.image.load(f"{root_folder}/GF/art/Win.png").convert_alpha()
Lose_pic=pygame.image.load(f"{root_folder}/GF/BG/2019summer_4_1 720.png").convert_alpha()  #pygame.image.load(f"{root_folder}/GF/BG/2019summer_2 720.png").convert_alpha()
Lose_description=pygame.image.load(f"{root_folder}/GF/art/Lose.png").convert_alpha()
M4A1_skill_pic=pygame.image.load(f"{root_folder}/GF/art/Lose.png").convert_alpha()




#M4A1图片初始定义
M4A1_list=M4A1_wait
M4A1 = M4A1_list[0]

#Nyto图片初始定义
nyto_list=nyto_wait
nyto = nyto_list[0]

#M4A1状态变量初始化
M4A1_rect = M4A1.get_rect(center=(screen_width // 4, screen_height // 2))
M4A1_left=False
M4A1_right=False
M4A1_up=False
M4A1_down=False
M4A1_ifattack=False
M4A1_ifshift=False
M4A1_dying=False
M4A1_alive=True
M4A1_movspeed=10
M4A1_ATK=5  #3
M4A1_MAXHP=1000
M4A1_HP=1000
dying_count=0
M4A1_frame=0
M4A1_deadcount=255

#nyto状态变量初始化
nyto_rect =nyto.get_rect(center=(1000, screen_height // 2))
nyto_ifattack=False
nyto_ifmove=False
nyto_MAXHP=2500
nyto_HP=2500
nyto_dying=False
nyto_alive=True
nyto_stay=[[1000, 360], [1000, 180], [1000,540],[720, 180], [720,540]]
nyto_speed=10
nyto_distance=0
nyto_ATK=20
nyto_attack_mode=0
nyto_attack_continue=False
nyto_skill4_count=0
nyto_attack3_bullet1_lastlose_range=15 #第一次skill4 phase1判定消除角度用
nyto_skill4_loop_count=0
nyto_frame=0
nyto_deadcount=255
nyto_time_set=0 #时间初始化次数 仅被使用一次

#初始图像输出
screen.blit(M4A1, M4A1_rect)
screen.blit(wait_background,(0,0))
screen.blit(wait_background_logo,(30,30))
screen.blit(subtitle,(80,130))
screen.blit(description,(517,550))
description_alpha=list(range(0, 256)) + list(range(255, -1, -1))
description_alpha_count=0 #用来取上面那个列表的
load_pic_alpha=7#过场动画后游戏场景的透明度


#M4A1判定点初始设定

player_rect=pygame.Rect(M4A1_rect.centerx-7,M4A1_rect.centery+17,10,10)
playerdot=pygame.image.load(f"{root_folder}/GF/M4A1/dot.png").convert_alpha()
playerdot_angle=0
plaerdot_rotated= pygame.transform.rotate(playerdot,playerdot_angle)
plaerdot_rotated.set_alpha(180) #透明度设置

#M4A1 子弹精灵类创建
class M4A1_Bullet(pygame.sprite.Sprite):
    def __init__(self,bullet_filepath,bullet_speed):
        #调用父类的初始化方法 每个都要有
        super().__init__()

        #定义对象属性
        self.image =pygame.image.load(bullet_filepath).convert_alpha()
        self.rect= self.image.get_rect()
        self.speed=bullet_speed
        #类方法
    def update(self):
        self.rect.x+=self.speed
        if self.rect.left>screen_width:
            self.kill()

#M4A1 子弹精灵组创建
M4A1_bullets=pygame.sprite.Group()

def M4A1_fire():
    M4A1_bullet=M4A1_Bullet(f"{root_folder}/GF/Bullet/M4A1/Bullet.png",40)
    M4A1_bullet.rect=pygame.Rect(M4A1_rect.right-80,M4A1_rect.centery+10,22,22)
    M4A1_bullets.add(M4A1_bullet)
    return

#nyto 定角度 定速 子弹精灵类创建 nyto_angle_Bullet  #零度起始线为水平向右 逆时针记角度
class nyto_angle_Bullet(pygame.sprite.Sprite):
    def __init__(self,bullet_filepath,bullet_speed,bullet_angle):
        #调用父类的初始化方法 每个都要有
        super().__init__()
        #定义对象属性
        self.image =pygame.image.load(bullet_filepath).convert_alpha()
        self.rect= self.image.get_rect()
        self.rect.center=nyto_rect.center
        self.speed=bullet_speed
        self.angle=bullet_angle
        self.x=float(self.rect.x)
        self.y=float(self.rect.y)
        #类方法
    def update(self):
        self.x-=self.speed*math.cos(math.radians(self.angle))
        self.y-=self.speed*math.sin(math.radians(self.angle))
        self.rect.x=self.x
        self.rect.y=self.y
        if self.rect.centerx >screen_width or self.rect.centerx <0 or self.rect.centery >screen_height or self.rect.centery <0:
            self.kill()

#nyto 自机狙子弹精灵类创建 nyto_Bullet_aimming
class nyto_aimming_Bullet(pygame.sprite.Sprite):
    def __init__(self,bullet_filepath,bullet_speed,start_rect,target_rect):
        #调用父类的初始化方法 每个都要有
        super().__init__()
        #定义对象属性
        self.image =pygame.image.load(bullet_filepath).convert_alpha()
        self.rect= start_rect
        self.speed=bullet_speed
        self.start_rect = start_rect
        self.target_rect = target_rect
        self.aimming_dx = start_rect.centerx - target_rect.centerx
        self.aimming_dy = start_rect.centery - target_rect.centery
        self.aimming_distance = math.hypot(self.aimming_dx, self.aimming_dy)

    def update(self):
        self.rect.x-=self.speed*(self.aimming_dx/self.aimming_distance)
        self.rect.y-=self.speed*(self.aimming_dy/self.aimming_distance)
        if self.rect.centerx >screen_width or self.rect.centerx <0 or self.rect.centery >screen_height or self.rect.centery <0:
            self.kill()

#nyto 幻影 子弹精灵类创建 nyto_phantom_Bullet
class nyto_phantom_Bullet(pygame.sprite.Sprite):
    def __init__(self,bullet_filepath,bullet_speed):
        #调用父类的初始化方法 每个都要有
        super().__init__()
        #定义对象属性
        self.image =pygame.image.load(bullet_filepath).convert_alpha()
        self.rect= self.image.get_rect()
        self.speed=bullet_speed
        self.frame=0
        self.phantom_hitbox=pygame.Rect(self.rect.left+85,self.rect.top+80,110,160)
        self.has_collided=False
        #类方法
    def update(self):
        global M4A1_HP
        if self.frame>=83:
            self.rect.x-=self.speed
            self.speed+=12
        if self.frame<=138:
            self.frame+=1
        self.image =phantom_dash[self.frame]
        if self.rect.left >screen_width or self.rect.right <0 or self.rect.top >screen_height or self.rect.bottom <0:
            self.kill()

    def phantom_collide(self):
        global M4A1_HP
        phantom_hitbox=pygame.Rect(self.rect.left+85,self.rect.top+80,110,160)
        #pygame.draw.rect(screen, (255, 0, 0), phantom_hitbox)
        if phantom_hitbox.colliderect(player_rect) and self.has_collided==False:
            M4A1_HP-=75
            self.has_collided=True
        return

#nyto 子弹精灵组创建  #子弹大小20
nyto_bullets_circle_20=pygame.sprite.Group()
#nyto 子弹精灵组创建  #子弹大小30
nyto_bullets_circle_30=pygame.sprite.Group()
#nyto 子弹精灵组创建  #子弹大小80
nyto_bullets_circle_80=pygame.sprite.Group()
#nyto 分身精灵组创建
nyto_bullets_phantom=pygame.sprite.Group()
#rect
#nyto_bullets_rect=pygame.sprite.Group()


#attack0 函数
def nyto_fire_mode0():
    global nyto_attack_continue #声明修改全局变量
    if nyto_attack_continue==False:
        nyto_attack_continue_random=random.random()
        nyto_mode0bullet_positiony=[-25.0,27.0]
        nyto_mode0bullet_positionx=[-20.0,-80.0,-140.0,-200.0]
        for i in range(0,4):
            for j in range(0,2):
                M4A1_rect_temp=player_rect.copy() #复制M4的rect
                nyto_attck0_bullet1_rect=pygame.Rect(nyto_rect.centerx+nyto_mode0bullet_positionx[i],nyto_rect.centery+nyto_mode0bullet_positiony[j],30,30)  #创建子弹起始rect
                M4A1_rect_temp.centerx+=nyto_mode0bullet_positionx[i]-(-20.0)
                M4A1_rect_temp.centery+=nyto_mode0bullet_positiony[j]  #目标点偏移
                nyto_attck0_bullet1=nyto_aimming_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",8,nyto_attck0_bullet1_rect,M4A1_rect_temp) #创建子弹类
                nyto_attck0_bullet1.rect.y+=(nyto_mode0bullet_positionx[i]-(-20))*(nyto_attck0_bullet1.aimming_dy/nyto_attck0_bullet1.aimming_distance) #y轴起始位置偏移
                nyto_bullets_circle_30.add(nyto_attck0_bullet1) #加入精灵组

    if nyto_attack_continue==True:
        for i in range(random.randint(0,5),360,10):
            nyto_attck0_bullet2=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",12,i)
            nyto_bullets_circle_30.add(nyto_attck0_bullet2)
            nyto_attack_continue=False
            nyto_attack_continue_random=0

    if nyto_attack_continue_random>0.25:
        nyto_attack_continue=True

    return

'''#skill3 函数
def nyto_fire_mode2():
    random_bullet_posiion=random.randint(0,36)
    nyto_mode2bullet_positiony=[0+ i*20 for i in range(720)]  #等差数组生成
    nyto_mode2bullet_positionx=[1250,1210,1170]
    bullet_posiion_offset=[20,0]
    for i in range(0,3):
        for j in range(0,2):
                nyto_attck2_bullet=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/nytoBulletrect 28.png",12,0)
                nyto_attck2_bullet.rect=pygame.Rect(nyto_mode2bullet_positionx[i],nyto_mode2bullet_positiony[random_bullet_posiion]+bullet_posiion_offset[j],28,28)
                nyto_bullets_rect.add(nyto_attck2_bullet)
    return'''

#skill3 函数
def nyto_fire_mode2():
    attck_add_random=random.random()
    random_bullet_posiiony=random.randint(0,25) #y轴随机点确定
    random_bullet_posiionx=random.randint(0,2) #x轴随机点确定
    nyto_phantom_bullet_positiony=[0+ i*20 for i in range(26)]   #26个y轴初始点
    nyto_phantom_bullet_positionx=[1000,900,800]  #三个x轴初始点
    phantom_bullet=nyto_phantom_Bullet(f"{root_folder}/GF/phantom/phantom_dash/0.png",40)  #精灵创建
    phantom_bullet.rect=pygame.Rect(nyto_phantom_bullet_positionx[random_bullet_posiionx],nyto_phantom_bullet_positiony[random_bullet_posiiony],280,280) #确定起始点 每次循环随机一个起始点 循环3次
    nyto_bullets_phantom.add(phantom_bullet) #加入精灵组
    if attck_add_random<=0.1:  #百分之25的几率生成一个时往下生成个
        for j in range(1,3):     #生成一个时往下生成两个
            phantom_bullet=nyto_phantom_Bullet(f"{root_folder}/GF/phantom/phantom_dash/0.png",40) #精灵创建
            phantom_bullet.rect=pygame.Rect(nyto_phantom_bullet_positionx[random_bullet_posiionx],nyto_phantom_bullet_positiony[random_bullet_posiiony]+j*100,280,280) #精灵rect再赋值
            #print(phantom_bullet.rect)
            nyto_bullets_phantom.add(phantom_bullet)  #加入精灵组
    return

#skill4阶段1函数
def nyto_fire_mode3_phase_1():
    global nyto_attack3_bullet1_lastlose_range
    if nyto_skill4_count==0:
        nyto_attack3_bullet1_range=[-90 + i*5 for i in range(72)]  #生成-90-270的列表
        nyto_attack3_bullet1_lose_range=random.randint(4,26) #消除30度的开头
        while nyto_attack3_bullet1_lose_range<nyto_attack3_bullet1_lastlose_range-8 or nyto_attack3_bullet1_lose_range> nyto_attack3_bullet1_lastlose_range+8: #与上一次消除角度不得相差40度
            nyto_attack3_bullet1_lose_range=random.randint(3,27)
        nyto_attack3_bullet1_lastlose_range=nyto_attack3_bullet1_lose_range
        del nyto_attack3_bullet1_range[nyto_attack3_bullet1_lose_range:nyto_attack3_bullet1_lose_range+6] #列表切片
        #print(  nyto_attack3_bullet1_range)
        for i in nyto_attack3_bullet1_range:
            nyto_attack3_bullet1=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",3,i)
            nyto_attack3_bullet1.rect.center=nyto_rect.center
            nyto_bullets_circle_30.add(nyto_attack3_bullet1)
    return

#skill4阶段2函数
def nyto_fire_mode3_phase_2():
    if nyto_skill4_count==0:
        nyto_attack3_bullet2_positionoffset_y=random.randint(-40,40)  #y轴随机偏移量生成
        nyto_attack3_bullet2_rect=pygame.Rect(nyto_rect.centerx,nyto_rect.centery+nyto_attack3_bullet2_positionoffset_y,20,20) #设定子弹初始rect
        nyto_attck3_bullet2=nyto_aimming_Bullet(f"{root_folder}/GF/Bullet/nyto/20.png",6,nyto_attack3_bullet2_rect,M4A1_rect) #创建子弹类
        nyto_bullets_circle_20.add(nyto_attck3_bullet2) #加入精灵组
    return

#skill4阶段3函数
def nyto_fire_mode3_phase_3():
    if nyto_skill4_count==1:
        for i in range(0,4):
            nyto_attack3_bullet3=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",3,random.randint(0,359)) #创建子弹类 随机选四个角度发射
            nyto_bullets_circle_30.add(nyto_attack3_bullet3) #加入精灵组
    return
def nyto_fire_mode3_phase_3_1():
    if nyto_skill4_count==1:
        for j in range(random.randint(0,10),360,12):
            nyto_attack3_bullet4=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/20.png",6,j) #创建子弹类 12个角度一发子弹
            nyto_bullets_circle_20.add(nyto_attack3_bullet4) #加入精灵组
    return

#skill4阶段4函数
def nyto_fire_mode3_phase_4():
    if nyto_skill4_count==1:
        if nyto_frame%2==0:
            nyto_fire_mode3_phase_4_bullet_angle=[180 + i*3 for i in range(61)] #180-360 61个
        else:
            nyto_fire_mode3_phase_4_bullet_angle=[0 + i*3 for i in range(61)] #0-180 61个
        for i in range(0,61): #0-60
            nyto_attack3_bullet5=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",9,nyto_fire_mode3_phase_4_bullet_angle[i])
            nyto_bullets_circle_30.add(nyto_attack3_bullet5) #加入精灵组
    return
#skill4阶段5函数
def nyto_fire_mode3_phase_5():
    if nyto_skill4_count==1:
        for i in range(nyto_frame%360,nyto_frame%360+360,25):  #步长25 帧为开始 360 度范围内取值
            nyto_attack3_bullet6=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",4,i)
            nyto_bullets_circle_30.add(nyto_attack3_bullet6) #加入精灵组
    return
#attack1函数
def nyto_fire_mode1_phase_1():
    for i in range(random.randint(0,10),370,11):  #步长11 帧为开始 360 度范围内取值
        nyto_attack1_bullet1=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/30.png",2,i)
        nyto_bullets_circle_30.add(nyto_attack1_bullet1) #加入精灵组
    return
#attack1阶段2函数
def nyto_fire_mode1_phase_2():
    for i in range(random.randint(0,10),415,25):  #步长25 帧为开始 415 度范围内取值
        nyto_attack1_bullet2=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/20.png",6,i)
        nyto_bullets_circle_20.add(nyto_attack1_bullet2) #加入精灵组
    nyto_attack1_bullet3_rect=pygame.Rect(nyto_rect.centerx,nyto_rect.centery,80,80)
    nyto_attack1_bullet3=nyto_aimming_Bullet(f"{root_folder}/GF/Bullet/nyto/80.png",14,nyto_attack1_bullet3_rect,player_rect)
    nyto_bullets_circle_80.add(nyto_attack1_bullet3)
    return

'''#skill3 函数
def nyto_fire_mode2():
    random_bullet_posiion=random.randint(0,36)
    nyto_mode2bullet_positiony=[0+ i*20 for i in range(720)]  #等差数组生成
    nyto_mode2bullet_positionx=[1250,1210,1170]
    bullet_posiion_offset=[20,0]
    for i in range(0,3):
        for j in range(0,2):
                nyto_attck2_bullet=nyto_angle_Bullet(f"{root_folder}/GF/Bullet/nyto/nytoBulletrect 28.png",12,0)
                nyto_attck2_bullet.rect=pygame.Rect(nyto_mode2bullet_positionx[i],nyto_mode2bullet_positiony[random_bullet_posiion]+bullet_posiion_offset[j],28,28)
                nyto_bullets_rect.add(nyto_attck2_bullet)
    return'''

#nyto碰撞精灵类创建
class nyto_hitbox(pygame.sprite.Sprite):
    def __init__(self,rect):
        super().__init__()
        self.rect = rect
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((255, 255, 255))  # 白色填充
    def update(self,new_rect):
        self.rect = new_rect


#nyto碰撞精灵组创建
nyto_hitboxs=pygame.sprite.Group()

#nyto判定点初始设定
enemy_rightlegrect=nyto_hitbox(pygame.Rect(nyto_rect.centerx+10,nyto_rect.centery+40,20,65))
enemy_leftlegrect=nyto_hitbox(pygame.Rect(nyto_rect.centerx-40,nyto_rect.centery+40,20,65))
enemy_bodyrect=nyto_hitbox(pygame.Rect(nyto_rect.centerx-20,nyto_rect.centery-20,30,60))
enemy_headrect=nyto_hitbox(pygame.Rect(nyto_rect.centerx-40,nyto_rect.centery-90,70,70))
#nyto判定点添加到碰撞精灵组
nyto_hitboxs.add(enemy_rightlegrect)
nyto_hitboxs.add(enemy_leftlegrect)
nyto_hitboxs.add(enemy_bodyrect)
nyto_hitboxs.add(enemy_headrect)


M4A1_head_pic=pygame.image.load(f"{root_folder}/GF/M4A1/pic_m4a1mod_n.png").convert_alpha()
M4A1_head_pic.set_alpha(240)
def draw_health_bar(name,current_health, max_health):
    health_ratio = current_health /  max_health
    if name == "M4A1":
        pygame.draw.rect(screen,(0,255,255), (120,710,200*health_ratio, 10)) #(0,255,255)为浅蓝色
    if name =="nyto":
        pygame.draw.rect(screen,(192,192,192), (140,50,1000*health_ratio,5))  #(192,192,192)为灰色
    return

#开始运行
running=True


while running:
    for event in pygame.event.get():
        #时间获取
        current_time=pygame.time.get_ticks()
        #退出
        if event.type == pygame.QUIT:
            running=False
                    #鼠标检测
        mouse_state=pygame.mouse.get_pressed()
        if mouse_state[0] == True:   #左键按下检测
            M4A1_ifattack=True
        if mouse_state[0] == False:   #左键抬起检测
            M4A1_ifattack=False

        if Game_START==False and LOSE==False and WIN==False and Game_LOAD==False:
            if mouse_state[0] == True:
                Game_LOAD=True
        if Game_START==False and (LOSE==True or WIN==True) and Game_LOAD==False:
            if mouse_state[0] == True:
                running=False
        #按键检测
        if event.type == pygame.KEYDOWN:
            #上下左右+wasd shift z 发起
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                    M4A1_left=True

            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    M4A1_right=True
            if event.key == pygame.K_UP or event.key == ord('w'):
                    M4A1_up=True
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                    M4A1_down=True
            if event.key == pygame.K_LSHIFT:
                    M4A1_ifshift=True
            '''if event.key == ord('z'): # z没法做攻击键  哪里有问题？？
                M4A1_ifattack=True
                print("Z")'''

        if event.type == pygame.KEYUP:
                #上下左右+wasd shift z 取消
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                    M4A1_left=False
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    M4A1_right=False
            if event.key == pygame.K_UP or event.key == ord('w'):
                    M4A1_up=False
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                    M4A1_down=False
            if event.key == pygame.K_LSHIFT:
                M4A1_ifshift=False
                '''if event.key == ord('z'):
                    M4A1_ifattack=False'''

        #进入游戏
    if Game_START:
        if nyto_time_set==0:
            nyto_move_time =current_time+random.randint(10000, 12000)
            nyto_attack_time =random.randint(1000, 2000)
            bgmusic_combat=pygame.mixer.music.load(f"{root_folder}/GF/Sound/M_19summer_song.wav")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)
            nyto_time_set+=1
            music_load_count+=1

        #M4A1移动状态判断
        if M4A1_dying==False and M4A1_list!=M4A1_win:
            if M4A1_ifattack==True and M4A1_right==True:
                M4A1_list=M4A1_moveattack
            elif M4A1_ifattack==True and M4A1_left==True:
                M4A1_list=M4A1_backattack
            elif M4A1_ifattack==True and (M4A1_up==True or M4A1_down==True):
                M4A1_list=M4A1_moveattack
            elif M4A1_ifattack==True:
                M4A1_list=M4A1_attack
            elif M4A1_right==True:
                M4A1_list=M4A1_move
            elif M4A1_left==True:
                M4A1_list=M4A1_back
            elif M4A1_up==True or M4A1_down==True:
                M4A1_list=M4A1_move
            else:
                M4A1_list=M4A1_wait

        if M4A1_dying==True and M4A1_list!=M4A1_win:
            M4A1_list=M4A1_die



        #M4A1速度判断（shift）实现
        if M4A1_dying==False and M4A1_list!=M4A1_win:
            if M4A1_ifshift==True:
                M4A1_movspeed=5
                M4A1.set_alpha(220)
            else:
                M4A1_movspeed=10
                M4A1.set_alpha(255)

        #M4A1位置更新+限制活动区域
        if M4A1_dying==False and M4A1_list!=M4A1_win:
            if M4A1_left==True and player_rect.left>=0:
                M4A1_rect.x-=M4A1_movspeed
            if M4A1_right==True and player_rect.right<=screen_width:
                M4A1_rect.x+=M4A1_movspeed
            if M4A1_up==True and player_rect.top>=0:
                M4A1_rect.y-=M4A1_movspeed
            if M4A1_down==True and player_rect.bottom<=screen_height:
                M4A1_rect.y+=M4A1_movspeed

        if M4A1_HP<=0 and dying_count==1:
                dying_count+=1
                M4A1=M4A1_die[0]


        #M4A1图片+BG输出
        screen.blit(background,(0,0))
        screen.blit(M4A1, M4A1_rect)
        #判定点输出
        if M4A1_ifshift==True and M4A1_dying==False and M4A1_list!=M4A1_win:
            plaerdot_rotated= pygame.transform.rotate(playerdot,playerdot_angle) #输出的是plaerdot_rotated
            playerdot_angle+=1 #每帧+1度
            playerdot_angle%=360 #防止帧数过大(M4A1_rect.centerx-70,M4A1_rect.centery-45,340,340)
            plaerdot_rotated_rect=plaerdot_rotated.get_rect(center=(player_rect.centerx,player_rect.centery))
            screen.blit(plaerdot_rotated,plaerdot_rotated_rect)
        #M4A1子弹输出
        if M4A1_list==M4A1_attack and M4A1_frame%len(M4A1_list) in [1,7,12] or M4A1_list==M4A1_moveattack and M4A1_frame%len(M4A1_list) in [1,5,10] or M4A1_list==M4A1_backattack and M4A1_frame%len(M4A1_list) in [1,7,12]:
            M4A1_fire()
            shot.play()

        M4A1_bullets.update()
        M4A1_bullets.draw(screen)

        #nyto移动 及 移动状态判定
        if current_time >= nyto_move_time:
            nyto_move_time = current_time + random.randint(9000, 10000)
            if nyto_ifattack==False:
                target=random.randint(0,4)
                targetx=nyto_stay[target][0]
                targety=nyto_stay[target][1]
                nyto_ifmove=True

        if nyto_ifmove==True and nyto_dying==False:
            dx = targetx - nyto_rect.centerx
            dy = targety - nyto_rect.centery
            nyto_distance = math.hypot(dx, dy)
            if nyto_distance>0:
                dx /= nyto_distance
                dy /= nyto_distance

            if nyto_distance > nyto_speed:
                nyto_rect.centerx += dx * nyto_speed
                nyto_rect.centery += dy * nyto_speed
            else:
                nyto_rect.centerx=nyto_stay[target][0]
                nyto_rect.centery=nyto_stay[target][1]
                nyto_ifmove=False

        #nyto攻击状态判定
        if current_time >= nyto_attack_time:
            nyto_attack_time =current_time + random.randint(500, 1000)

            if nyto_ifmove==False and nyto_ifattack==False and nyto_attack_mode!=3:
                nyto_attack_mode=random.choice([0,1,2])
                nyto_ifattack=True


        #M4A1子弹与nyto的碰撞判定
        if pygame.sprite.groupcollide(M4A1_bullets, nyto_hitboxs,True, False):
            nyto_HP-=M4A1_ATK
            #print(nyto_HP)
            #nyto血量小于百分之50且skill4发动次数为零 ifattack置True
            if nyto_HP<=nyto_MAXHP*0.5 and nyto_skill4_count==0:
                nyto_ifattack=True
                nyto_attack_mode=3
                M4A1_ATK=3
            #nyto血量小于百分之50且skill4发动次数为零 ifattack置True
            elif nyto_HP<=nyto_MAXHP*0.25 and nyto_skill4_count==1:
                nyto_ifattack=True
                nyto_attack_mode=3
            #死亡动画加载
            if nyto_HP<=0:
                nyto_dying=True
                nyto_frame=-1
                nyto_rect.x+=120
                nyto_hitboxs.empty()

        #nyto攻击结束判定
        if nyto_attack_continue==False and nyto==nyto_attack1[49]:
            nyto_ifattack=False
        elif nyto==nyto_skill3[66]:
            nyto_ifattack=False
        elif nyto==nyto_attack2[66]:
            nyto_ifattack=False
        #第一次skill4结束后次数加一
        elif nyto==nyto_skill4[638] and nyto_skill4_count==0:
            nyto_ifattack=False
            nyto_attack_mode=1
            nyto_skill4_count+=1
        elif nyto==nyto_skill4[600] and nyto_skill4_count==1 and nyto_skill4_loop_count<2:
                nyto_frame=67
                nyto_skill4_loop_count+=1
        elif nyto==nyto_skill4[638] and nyto_skill4_count==1 and nyto_skill4_loop_count==2:
            nyto_ifattack=False
            nyto_attack_mode=1
            nyto_skill4_count+=1

        #Nyto攻击模式判定
        if nyto_dying==False:
            if nyto_ifmove==True and nyto_list!=nyto_ifmove:
                nyto_list=nyto_move
                nyto_frame=0
            elif nyto_ifattack==True:
                if nyto_attack_mode==3 and nyto_list!=nyto_skill4 and nyto_skill4_count<=1:
                    nyto_list=nyto_skill4
                    nyto_frame=0
                elif nyto_attack_mode==0 and  nyto_list!=nyto_attack1:
                    nyto_list=nyto_attack1
                    nyto_frame=0
                elif nyto_attack_mode==1 and  nyto_list!=nyto_attack2:
                    nyto_list=nyto_attack2
                    nyto_frame=0
                elif nyto_attack_mode==2 and nyto_list!=nyto_skill3:
                    nyto_list=nyto_skill3
                    nyto_frame=0
            elif nyto_ifmove==False and nyto_ifattack==False:
                nyto_list=nyto_wait

        #Nyto图片输出
        screen.blit(nyto, nyto_rect)

        #nyto子弹输出
        if nyto_list==nyto_attack1 and (nyto_frame%len(nyto_list)==31): #攻击1
            nyto_fire_mode0()
        elif nyto_list==nyto_skill3 and nyto_frame%len(nyto_list) in [19,31,46]: #技能3
            nyto_fire_mode2()
        elif nyto_list==nyto_skill4 and nyto_frame%len(nyto_list) in [71,121,170,215,245,285,355,375,435,455,475,495,550,570,585,605] and nyto_skill4_count==0: #技能4 第一次
            nyto_fire_mode3_phase_1()
        elif nyto_list==nyto_skill4 and nyto_frame%len(nyto_list) in [610+ i*2 for i in range(15)] and nyto_skill4_count==0: #第610张开始 12枚子弹
            nyto_fire_mode3_phase_2()
        elif nyto_list==nyto_skill4 and nyto_frame%len(nyto_list) in [67+ i*2 for i in range(216)] and nyto_skill4_count==1 and nyto_skill4_loop_count==0: #技能4 第二次 第一次循环 loop是60-600
            nyto_fire_mode3_phase_3()
            if nyto_frame%len(nyto_list) in [131+ i*64 for i in range(7)]:   #7个圆弧弹幕
                nyto_fire_mode3_phase_3_1()
        elif nyto_list==nyto_skill4 and nyto_frame%len(nyto_list) in [67+ i*59 for i in range(9)] and nyto_skill4_count==1 and nyto_skill4_loop_count==1: #技能4 第二次 第二次循环
            nyto_fire_mode3_phase_4()
        elif nyto_list==nyto_skill4 and nyto_frame%len(nyto_list) in [62+ i*7 for i in range(77)] and nyto_skill4_count==1 and nyto_skill4_loop_count==2: #技能4 第二次 第三次循环
            nyto_fire_mode3_phase_5()
        elif nyto_list==nyto_attack2 and nyto_frame%len(nyto_list) in [32,50]: #attack2
            if nyto_frame%len(nyto_list)==32:
                nyto_fire_mode1_phase_1()
            else:
                nyto_fire_mode1_phase_2()


        #nyto子弹刷新
        nyto_bullets_circle_20.update()
        nyto_bullets_circle_30.update()
        nyto_bullets_circle_80.update()
        nyto_bullets_circle_20.draw(screen)
        nyto_bullets_circle_30.draw(screen)
        nyto_bullets_circle_80.draw(screen)
        ##nyto_bullets_rect.draw(screen)
        nyto_bullets_phantom.update()
        for sprite in nyto_bullets_phantom:
            sprite.image.set_alpha(130)
            screen.blit(sprite.image, sprite.rect)
            sprite.phantom_collide()
        #nyto子弹伤害判定
        for sprite in nyto_bullets_circle_20:
            if(math.hypot(sprite.rect.centerx - player_rect.centerx,sprite.rect.centery - player_rect.centery)<=10):
                M4A1_HP-=20
                sprite.kill()
        for sprite in nyto_bullets_circle_30:
            if(math.hypot(sprite.rect.centerx - player_rect.centerx,sprite.rect.centery - player_rect.centery)<=20):
                M4A1_HP-=30
                sprite.kill()
        for sprite in nyto_bullets_circle_80:
            if(math.hypot(sprite.rect.centerx - player_rect.centerx,sprite.rect.centery - player_rect.centery)<=60):
                M4A1_HP-=80
                sprite.kill()

        if M4A1_HP<=0 and dying_count==0:
                dying_count+=1
                M4A1_dying=True
                M4A1_frame=-1
                M4A1_rect.centerx+=50


        #判定点位置更新
        player_rect=pygame.Rect(M4A1_rect.centerx-7,M4A1_rect.centery+17,10,10)
        nyto_hitbox.update(enemy_rightlegrect,pygame.Rect(nyto_rect.centerx+10,nyto_rect.centery+40,20,65))
        nyto_hitbox.update(enemy_leftlegrect,pygame.Rect(nyto_rect.centerx-40,nyto_rect.centery+40,20,65))
        nyto_hitbox.update(enemy_bodyrect,pygame.Rect(nyto_rect.centerx-20,nyto_rect.centery-20,30,60))
        nyto_hitbox.update(enemy_headrect,pygame.Rect(nyto_rect.centerx-40,nyto_rect.centery-90,70,70))

        #绘制判定点
        #pygame.draw.rect(screen,(255,255,255),player_rect)
        #nyto_hitboxs.draw(screen)
        #绘制血条
        draw_health_bar("nyto",nyto_HP,nyto_MAXHP)
        draw_health_bar("M4A1",M4A1_HP,M4A1_MAXHP)
        screen.blit(M4A1_head_pic,(0,600))
        #nyto临死判定+死亡判定 ##这里加载的都是下一循环的动画内容？？？
        if nyto_dying==True:
            nyto_list=nyto_die
            if nyto==nyto_die[127]:
                nyto_alive=False
        #M4A1死亡判定
        if M4A1==M4A1_die[136]:
            M4A1_alive=False


        #切换到下一帧+死亡后计时
        if nyto_alive==True:
            nyto_frame+=1
        else:
            nyto.set_alpha(nyto_deadcount)
            if nyto_deadcount>=0:
                nyto_deadcount-=6

        if M4A1_alive==True:
            M4A1_frame+=1
        else:
            M4A1.set_alpha(M4A1_deadcount)
            if M4A1_deadcount>=0:
                M4A1_deadcount-=6


        #菜单切换
        if nyto_deadcount<=0:
            if M4A1_list!=M4A1_win:
                M4A1_frame=0
                M4A1_list=M4A1_win
            elif M4A1==M4A1_win[141]:
                WIN=True
                pygame.mixer.music.fadeout(3000)
        elif M4A1_deadcount<=0:
            LOSE=True
            pygame.mixer.music.fadeout(1000)

        nyto = nyto_list[nyto_frame%len(nyto_list)]
        M4A1 = M4A1_list[M4A1_frame%len(M4A1_list)]

    #等待界面
    if Game_START==False and LOSE==False and WIN==False and Game_LOAD==False:
        if music_load_count==0:
            pygame.mixer.music.load(f"{root_folder}/GF/Sound/M_19summer_zombie_h.ogg")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1)
            music_load_count+=1
        description.set_alpha(description_alpha[description_alpha_count%len(description_alpha)])#不断遍历
        description_alpha_count+=3
        screen.blit(wait_background,(0,0))
        screen.blit(wait_background_logo,(30,30))
        screen.blit(subtitle,(80,130))
        screen.blit(description,(517,550))

    if Game_LOAD==True:
        load_pic=load_pic_list[load_pic_num]
        if load_pic_num==394:
            Game_START=True
            Game_LOAD=False
        if load_pic_num>=364:
            temp_M4A1=M4A1
            temp_M4A1.set_alpha(load_pic_alpha)
            temp_nyto=nyto
            temp_nyto.set_alpha(load_pic_alpha)
            temp_background=background
            temp_background.set_alpha(load_pic_alpha)
            screen.blit(temp_background,(0,0))
            screen.blit(temp_M4A1,(M4A1_rect.x,M4A1_rect.y))
            screen.blit(temp_nyto,(nyto_rect.x,nyto_rect.y))
            load_pic_alpha+=8
            #print(load_pic_alpha)
        load_pic.set_alpha(255-load_pic_alpha)
        screen.blit(load_pic,(0,0))
        load_pic_num+=1
        #print(load_pic_num)


    #胜利/失败界面
    if WIN==True:
        if music_load_count==2:
            pygame.mixer.music.load(f"{root_folder}/GF/Sound/Win.wav")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1,fade_ms=2000)
            music_load_count+=1
        Game_START=False
        screen.blit(Win_pic,(0,0))
        screen.blit(Win_description,(290,200))

    elif LOSE==True:
        if music_load_count==2:
            pygame.mixer.music.load(f"{root_folder}/GF/Sound/Lose.wav")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1,fade_ms=2000)
            music_load_count+=1
        Game_START=False
        screen.blit(Lose_pic,(0,0))
        screen.blit(Lose_description,(190,300))

    #死亡
    if nyto_alive==False:
        #print("Win")
        pass
    if M4A1_alive==False:
        #print("Lose")
        pass
    # 更新屏幕
    pygame.display.flip()
    clock.tick(fps)