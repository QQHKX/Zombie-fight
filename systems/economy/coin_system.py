import pygame
import os
import json
from config import *
from core.resource_manager import ResourceManager

class CoinSystem:
    """金币系统类，管理金币的获取、消费和存储"""
    
    def __init__(self, game):
        """初始化金币系统
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.coins = 0  # 初始化为0，由SaveManager控制实际金币数量
        
        # 加载金币图标
        self.coin_icon = self._create_coin_icon()
        
        # 加载金币音效
        self.coin_sound = ResourceManager.load_sound(os.path.join(SOUND_DIR, "hit.mp3"))  # 临时使用hit音效
        if self.coin_sound:
            self.coin_sound.set_volume(0.3)
        
        # 金币获取动画
        self.coin_animations = []
    
    def _create_coin_icon(self):
        """创建金币图标
        
        Returns:
            Surface: 金币图标Surface
        """
        # 创建一个圆形的金币图标
        icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(icon, (255, 215, 0), (15, 15), 15)  # 金色圆形
        pygame.draw.circle(icon, (255, 165, 0), (15, 15), 12, 2)  # 橙色边框
        return icon
    
    def add_coins(self, amount, position=None):
        """增加金币数量
        
        Args:
            amount: 增加的金币数量
            position: 金币获取位置，用于显示动画
        """
        self.coins += amount
        
        # 播放金币音效
        if self.coin_sound:
            self.coin_sound.play()
        
        # 如果提供了位置，添加金币获取动画
        if position:
            self.add_coin_animation(position, amount)
    
    def spend_coins(self, amount):
        """消费金币
        
        Args:
            amount: 消费的金币数量
        
        Returns:
            bool: 是否消费成功
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def add_coin_animation(self, position, amount):
        """添加金币获取动画
        
        Args:
            position: 金币获取位置
            amount: 获取的金币数量
        """
        self.coin_animations.append({
            "position": position,
            "amount": amount,
            "time": 0,
            "duration": 60,  # 动画持续60帧
            "start_y": position[1],
            "target_y": 50  # 金币图标的Y坐标
        })
    
    def update_animations(self):
        """更新金币动画"""
        for anim in self.coin_animations[:]:
            anim["time"] += 1
            if anim["time"] >= anim["duration"]:
                self.coin_animations.remove(anim)
    
    def render_animations(self, screen):
        """渲染金币动画
        
        Args:
            screen: 游戏屏幕Surface
        """
        for anim in self.coin_animations:
            # 计算动画进度
            progress = anim["time"] / anim["duration"]
            
            # 计算当前位置（从获取位置移动到金币图标位置）
            x = anim["position"][0] + (SCREEN_WIDTH - 100 - anim["position"][0]) * progress
            y = anim["start_y"] + (anim["target_y"] - anim["start_y"]) * progress
            
            # 计算透明度（逐渐消失）
            alpha = 255 * (1 - progress)
            
            # 创建带透明度的金币图标
            icon = self.coin_icon.copy()
            icon.set_alpha(alpha)
            
            # 绘制金币图标
            screen.blit(icon, (x - 15, y - 15))  # 居中显示
            
            # 绘制金币数量
            font = pygame.font.Font(None, 24)
            text = font.render(f"+{anim['amount']}", True, (255, 255, 255))
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(x + 20, y))
            screen.blit(text, text_rect)
    
    def save_coins(self):
        """保存金币数据（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，金币数据由SaveManager统一管理
        pass

    def load_coins(self):
        """加载金币数据（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，金币数据由SaveManager统一管理
        pass

    def reset(self):
        """重置金币系统（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，金币数据由SaveManager统一管理
        pass