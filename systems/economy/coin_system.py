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
        self.coins = 30  # 初始金币数设置为30
        
        # 加载金币图标
        self.coin_icon = self._create_coin_icon()
        
        # 加载金币音效
        self.coin_sound = ResourceManager.load_sound(os.path.join(SOUND_DIR, "hit.mp3"))  # 临时使用hit音效
        if self.coin_sound:
            self.coin_sound.set_volume(0.3)
        
        # 金币获取动画
        self.coin_animations = []
        
        # 加载存档数据
        self.load_coins()
    
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
        
        # 添加金币获取动画
        if position:
            self.add_coin_animation(amount, position)
        
        # 保存金币数据
        self.save_coins()
    
    def spend_coins(self, amount):
        """消费金币
        
        Args:
            amount: 消费的金币数量
        
        Returns:
            bool: 是否消费成功
        """
        if self.coins >= amount:
            self.coins -= amount
            self.save_coins()
            return True
        return False
    
    def add_coin_animation(self, amount, position):
        """添加金币获取动画
        
        Args:
            amount: 获取的金币数量
            position: 金币获取位置
        """
        self.coin_animations.append({
            "amount": amount,
            "position": position,
            "target": (100, 50),  # 金币UI位置
            "progress": 0,
            "duration": 30,  # 动画持续帧数
            "scale": 1.0,
            "alpha": 255
        })
    
    def update_animations(self):
        """更新金币动画"""
        for anim in self.coin_animations[:]:  # 使用副本进行迭代
            # 更新动画进度
            anim["progress"] += 1
            
            # 计算动画位置（使用缓动函数使动画更平滑）
            progress = anim["progress"] / anim["duration"]
            
            # 使用二次缓动函数
            eased_progress = progress * (2 - progress)
            
            # 计算当前位置
            start_x, start_y = anim["position"]
            target_x, target_y = anim["target"]
            current_x = start_x + (target_x - start_x) * eased_progress
            current_y = start_y + (target_y - start_y) * eased_progress
            anim["position"] = (current_x, current_y)
            
            # 缩放和透明度变化
            anim["scale"] = max(0.5, 1.0 - 0.5 * progress)
            anim["alpha"] = max(0, 255 - int(255 * progress))
            
            # 移除完成的动画
            if anim["progress"] >= anim["duration"]:
                self.coin_animations.remove(anim)
    
    def render_animations(self, screen):
        """渲染金币动画
        
        Args:
            screen: 游戏屏幕
        """
        for anim in self.coin_animations:
            # 缩放金币图标
            scaled_size = int(30 * anim["scale"])
            scaled_icon = pygame.transform.scale(self.coin_icon, (scaled_size, scaled_size))
            
            # 设置透明度
            scaled_icon.set_alpha(anim["alpha"])
            
            # 计算绘制位置（居中）
            x, y = anim["position"]
            draw_x = x - scaled_size // 2
            draw_y = y - scaled_size // 2
            
            # 绘制金币图标
            screen.blit(scaled_icon, (draw_x, draw_y))
            
            # 绘制金币数量文本
            if anim["amount"] > 1:
                font = pygame.font.Font(REGULAR_FONT, int(20 * anim["scale"]))
                text = font.render(f"+{anim['amount']}", True, (255, 255, 255))
                text.set_alpha(anim["alpha"])
                text_rect = text.get_rect(center=(x + 20, y))
                screen.blit(text, text_rect)
    
    def save_coins(self):
        """保存金币数据"""
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saves")
        
        # 确保保存目录存在
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 保存到文件
        save_path = os.path.join(save_dir, "coins.json")
        try:
            with open(save_path, "w") as f:
                json.dump({"coins": self.coins}, f)
        except Exception as e:
            print(f"保存金币数据失败: {e}")
    
    def load_coins(self):
        """加载金币数据"""
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saves")
        save_path = os.path.join(save_dir, "coins.json")
        
        # 如果保存文件存在，加载数据
        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as f:
                    data = json.load(f)
                    self.coins = data.get("coins", 0)
            except Exception as e:
                print(f"加载金币数据失败: {e}")
    
    def reset(self):
        """重置金币系统"""
        self.coins = 3000  # 将初始金币数设置为30
        self.coin_animations = []
        self.save_coins()