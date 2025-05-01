import pygame

from config import *

class Particle(pygame.sprite.Sprite):
    """粒子效果类，用于显示打击效果"""
    
    def __init__(self, x, y, color=(255, 255, 0), size=5, speed_x=0, speed_y=0, lifetime=20):
        """初始化粒子对象
        
        Args:
            x: 粒子的x坐标
            y: 粒子的y坐标
            color: 粒子颜色
            size: 粒子大小
            speed_x: x方向速度
            speed_y: y方向速度
            lifetime: 粒子生命周期（帧数）
        """
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifetime = lifetime
        self.age = 0
        
    def update(self):
        """更新粒子状态"""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.age += 1
        
        # 随着年龄增长，粒子变得更透明
        alpha = 255 * (1 - self.age / self.lifetime)
        self.image.set_alpha(alpha)
        
        # 如果粒子寿命结束，将其移除
        if self.age >= self.lifetime:
            self.kill()
