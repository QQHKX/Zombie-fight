import pygame

from config import *
from core.resource_manager import ResourceManager

class Bullet(pygame.sprite.Sprite):
    """子弹类，表示玩家发射的子弹"""
    
    def __init__(self, x, y, speed):
        """初始化子弹对象
        
        Args:
            x: 子弹的x坐标
            y: 子弹的y坐标
            speed: 子弹的移动速度
        """
        super().__init__()
        self.image = ResourceManager.load_image(BULLET_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 20
        self.height = 20
        self.speed = speed
    
    def update(self):
        """更新子弹位置"""
        self.rect.x += self.speed
        
        # 如果子弹超出屏幕，将其移除
        if self.rect.left > SCREEN_WIDTH:
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

