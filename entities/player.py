import pygame
import time

from config import *
from core.resource_manager import ResourceManager

class Player(pygame.sprite.Sprite):
    """玩家类，表示玩家控制的大炮"""
    
    def __init__(self):
        """初始化玩家对象"""
        super().__init__()
        self.original_image = ResourceManager.load_image(CANNON_IMAGE)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.initial_x = 20  # 设置初始x坐标，留出后坐力空间
        self.rect.x = self.initial_x
        self.rect.y = SCREEN_HEIGHT // 2 - self.rect.height // 2
        self.score = 0
        
        # 发射动画相关
        self.is_firing = False
        self.firing_frame = 0
        self.firing_max_frames = 15  # 增加帧数使动画更流畅
        self.recoil_offset = 0  # 后坐力位移
        self.original_center = None  # 存储原始中心点
        
        # 得分动画相关
        self.score_animations = []
    
    def update(self, mouse_y=None, mouse_x=None):
        """更新玩家位置和动画状态
        
        Args:
            mouse_y: 鼠标的y坐标，如果为None则只更新动画状态
            mouse_x: 鼠标的x坐标，如果为None则不更新水平位置
        """
        # 如果提供了鼠标位置，则更新炮台的位置
        if mouse_y is not None:
            # 如果正在发射动画中，记录新的目标y坐标
            if self.is_firing and self.original_center is not None:
                # 更新原始中心点的y坐标
                self.original_center = (self.original_center[0], mouse_y - self.rect.height // 2 + self.rect.height // 2)
            else:
                # 根据鼠标位置更新大炮的y坐标
                self.rect.y = mouse_y - self.rect.height // 2
            
            # 确保大炮不会超出屏幕垂直边界
            target_y = mouse_y - self.rect.height // 2
            if target_y < 0:
                target_y = 0
            elif target_y + self.rect.height > SCREEN_HEIGHT:
                target_y = SCREEN_HEIGHT - self.rect.height
                
            # 如果不在发射动画中，直接更新垂直位置
            if not self.is_firing:
                self.rect.y = target_y
        
        # 更新水平位置（如果提供了鼠标x坐标）
        if mouse_x is not None:
            # 计算目标x坐标，但限制不能超过屏幕宽度的一半
            max_x = SCREEN_WIDTH // 2 - self.rect.width // 2
            target_x = min(mouse_x - self.rect.width // 2, max_x)
            target_x = max(0, target_x)  # 确保不会小于0
            
            # 如果正在发射动画中，更新原始中心点的x坐标
            if self.is_firing and self.original_center is not None:
                self.original_center = (target_x + self.rect.width // 2, self.original_center[1])
                # 后坐力位移是相对于初始位置的，所以更新初始位置
                self.initial_x = target_x
            else:
                # 直接更新位置
                self.rect.x = target_x
                self.initial_x = target_x
        
        # 更新发射动画
        if self.is_firing:
            self.firing_frame += 1
            # 使用缓动函数使动画更加平滑
            progress = self.firing_frame / self.firing_max_frames
            
            # 前半段使用快速缓出函数，后半段使用缓入函数
            if progress < 0.5:
                # 前半段：快速后退（后坐力）
                half_progress = progress * 2  # 0-0.5 映射到 0-1
                eased_progress = 1 - (1 - half_progress) * (1 - half_progress)  # 二次缓出
                self.recoil_offset = -12 * eased_progress  # 减小后坐力位移
            else:
                # 后半段：缓慢恢复
                half_progress = (progress - 0.5) * 2  # 0.5-1 映射到 0-1
                eased_progress = half_progress * half_progress  # 二次缓入
                self.recoil_offset = -12 * (1 - eased_progress)  # 减小后坐力恢复
            
            # 发射动画效果：缩放和旋转
            if progress < 0.3:  # 前30%的时间快速缩小
                scale_factor = 1.0 - 0.08 * (progress / 0.3)  # 减小缩放幅度
            else:  # 后70%的时间缓慢恢复
                recovery_progress = (progress - 0.3) / 0.7
                scale_factor = 0.92 + 0.08 * recovery_progress  # 减小缩放幅度
                
            rotation_angle = -5 * self.recoil_offset / -12  # 减小旋转角度
            
            # 缩放原始图像
            scaled_image = pygame.transform.scale(self.original_image, 
                                               (int(self.original_image.get_width() * scale_factor),
                                                int(self.original_image.get_height() * scale_factor)))
            
            # 旋转缩放后的图像
            self.image = pygame.transform.rotate(scaled_image, rotation_angle)
            
            # 保持炮台位置跟随鼠标移动，同时应用后坐力位移
            if self.original_center is None:
                self.original_center = self.rect.center
                
            self.rect = self.image.get_rect()
            self.rect.centery = self.original_center[1]  # 使用当前的垂直位置
            self.rect.x = self.initial_x + self.recoil_offset  # 基于初始位置应用后坐力位移
            
            # 动画结束，恢复原始图像
            if self.firing_frame >= self.firing_max_frames:
                self.is_firing = False
                self.firing_frame = 0
                self.recoil_offset = 0
                self.image = self.original_image.copy()
                self.rect = self.image.get_rect()
                self.rect.centery = self.original_center[1]
                self.rect.x = self.initial_x
                self.original_center = None  # 重置原始中心点
    
    def fire(self):
        """触发发射动画"""
        self.is_firing = True
        self.firing_frame = 0
        self.original_center = self.rect.center  # 记录发射前的中心位置
        # 立即应用初始后坐力效果，使动画更加连贯
        self.recoil_offset = 0
    
    def add_score_animation(self, score, position):
        """添加得分动画
        
        Args:
            score: 增加的得分
            position: 动画起始位置
        """
        self.score_animations.append({
            "score": score,
            "position": position,
            "frame": 0
        })
