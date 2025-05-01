import pygame
import random
from entities.zombies.base_zombie import BaseZombie

class FastZombie(BaseZombie):
    """快速僵尸类，速度快但生命值低"""
    
    def __init__(self, y, level=1):
        """初始化快速僵尸
        
        Args:
            y: 僵尸的y坐标
            level: 僵尸等级
        """
        super().__init__(y, level, "fast")
        
        # 快速僵尸特有属性
        self.description = "快速僵尸，移动速度快但生命值低"
        self.dash_cooldown = 0  # 冲刺冷却时间
        self.is_dashing = False  # 是否正在冲刺
        self.dash_speed_multiplier = 2.0  # 冲刺速度倍数
        self.original_speed = self.speed  # 记录原始速度
        
    def update(self):
        """更新快速僵尸状态和位置"""
        # 处理冲刺逻辑
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            
            # 结束冲刺
            if self.is_dashing and self.dash_cooldown <= 0:
                self.is_dashing = False
                self.speed = self.original_speed
        elif random.random() < 0.005 and not self.is_dashing:  # 0.5%的概率触发冲刺
            self.special_ability()
        
        # 调用父类的update方法
        return super().update()
    
    def special_ability(self):
        """快速僵尸的特殊能力：短暂冲刺"""
        if self.dash_cooldown <= 0:
            self.is_dashing = True
            self.original_speed = self.speed
            self.speed *= self.dash_speed_multiplier
            self.dash_cooldown = 60  # 冲刺持续60帧，约1秒
            
            # 冲刺特效（可以在这里添加粒子效果等）