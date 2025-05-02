import pygame

from config import *
from core.resource_manager import ResourceManager

class Bullet(pygame.sprite.Sprite):
    """子弹类，由玩家发射"""
    
    # 类变量，所有实例共享
    bullet_image = None
    
    @classmethod
    def preload_image(cls):
        """预加载子弹图片，游戏启动时调用一次"""
        if cls.bullet_image is None:
            cls.bullet_image = ResourceManager.load_image(BULLET_IMAGE)
    
    def __init__(self, x, y, target_y, speed=None, damage=None):
        """初始化子弹对象
        
        Args:
            x: 子弹的初始x坐标
            y: 子弹的初始y坐标
            target_y: 子弹的目标y坐标，用于计算子弹的角度
            speed: 子弹的速度，如果为None则使用默认值5
            damage: 子弹的伤害值，如果为None则使用默认值1
        """
        super().__init__()
        
        # 确保子弹图片已预加载
        if Bullet.bullet_image is None:
            Bullet.preload_image()
        
        # 使用预加载的子弹图像
        self.original_image = Bullet.bullet_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 子弹属性
        self.speed = 5 if speed is None else speed
        self.damage = 1 if damage is None else damage
        
        # 子弹只水平移动，不再有垂直分量
        self.vx = self.speed  # 水平速度固定
        self.vy = 0  # 垂直速度为0，子弹水平飞行
    
    def update(self):
        """更新子弹位置"""
        # 更新子弹位置
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # 如果子弹超出屏幕，则移除
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or \
           self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()
    
    def check_hit(self, zombie):
        """检测子弹是否击中僵尸
        
        Args:
            zombie: 僵尸对象
            
        Returns:
            bool: 如果击中返回True，否则返回False
        """
        # 使用pygame的碰撞检测函数
        return pygame.sprite.collide_rect(self, zombie)

