import pygame
import os
import random

from config import *
from core.resource_manager import ResourceManager

class Zombie(pygame.sprite.Sprite):
    """僵尸类，表示游戏中的敌人"""
    
    def __init__(self, y, speed):
        """初始化僵尸对象
        
        Args:
            y: 僵尸的y坐标
            speed: 僵尸的移动速度
        """
        super().__init__()
        self.speed = speed
        self.rect = pygame.Rect(SCREEN_WIDTH, y, 180, 180)
        # 创建一个比视觉大小小一些的碰撞区域，并向后移动一点
        self.hit_rect = pygame.Rect(0, 0, 140, 160)  # 碰撞区域比视觉区域小
        self.update_hit_rect()  # 初始化碰撞区域位置
        
        self.state = ZOMBIE_MOVE
        self.index = 0
        
        # 加载僵尸移动动画帧
        self.move_frames = []
        for i in range(1, 14):
            frame_path = os.path.join(ZOMBIE_MOVE_DIR, f"zombie_move_{i:02d}.png")
            self.move_frames.append(ResourceManager.load_image(frame_path))
        
        # 当前显示的帧
        self.image = self.move_frames[0]
    
    def update(self):
        """更新僵尸状态和位置"""
        # 更新动画帧，动画速度与移动速度成正比
        if self.state == ZOMBIE_MOVE:
            # 根据移动速度调整动画速度，速度越快，动画播放越快
            animation_speed_factor = max(1, self.speed) / 2.31  # 基准速度为3时动画正常播放
            
            # 计算当前应该显示的帧
            frame_index = int(self.index * animation_speed_factor) % len(self.move_frames)
            self.image = self.move_frames[frame_index]
            
            # 更新位置
            self.rect.x -= self.speed
            # 更新碰撞区域位置
            self.update_hit_rect()
        
        self.index += 1
        
        # 如果僵尸到达屏幕左边缘，返回True表示游戏结束
        if self.rect.right <= 0:
            return True
        return False
        
    def update_hit_rect(self):
        """更新碰撞区域位置，使其位于僵尸图像内部并向后移动一点"""
        # 将碰撞区域放在僵尸图像的中心，但向后移动一点
        self.hit_rect.centerx = self.rect.centerx + 20  # 向后移动20像素
        self.hit_rect.centery = self.rect.centery
        
    def get_hit_rect(self):
        """获取用于碰撞检测的矩形区域"""
        return self.hit_rect



