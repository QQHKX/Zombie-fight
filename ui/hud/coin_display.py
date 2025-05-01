import pygame
import os

class CoinDisplay:
    """金币显示类，负责在游戏界面上显示金币数量和相关动画"""
    
    def __init__(self, game, coin_system):
        """初始化金币显示
        
        Args:
            game: 游戏主类实例
            coin_system: 金币系统实例
        """
        self.game = game
        self.coin_system = coin_system
        
        # 加载金币图标
        self.coin_image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.coin_image, (255, 215, 0), (15, 15), 15)  # 金色圆形
        pygame.draw.circle(self.coin_image, (255, 165, 0), (15, 15), 12, 2)  # 橙色边框
        
        # 金币UI位置
        self.position = (50, 40)
        self.text_position = (90, 45)
        
        # 金币获取动画效果
        self.pulse_effect = False
        self.pulse_frame = 0
        self.pulse_max_frames = 20
        self.pulse_scale = 1.0
    
    def update(self):
        """更新金币显示状态"""
        # 更新脉冲效果
        if self.pulse_effect:
            self.pulse_frame += 1
            progress = self.pulse_frame / self.pulse_max_frames
            
            # 计算缩放因子（先放大后恢复）
            if progress < 0.5:
                self.pulse_scale = 1.0 + 0.3 * (progress * 2)  # 0.0-0.5 映射到 1.0-1.3
            else:
                self.pulse_scale = 1.3 - 0.3 * ((progress - 0.5) * 2)  # 0.5-1.0 映射到 1.3-1.0
            
            # 结束脉冲效果
            if self.pulse_frame >= self.pulse_max_frames:
                self.pulse_effect = False
                self.pulse_frame = 0
                self.pulse_scale = 1.0
    
    def trigger_pulse(self):
        """触发金币图标的脉冲效果（当获得金币时）"""
        self.pulse_effect = True
        self.pulse_frame = 0
    
    def render(self, screen):
        """渲染金币显示
        
        Args:
            screen: 游戏屏幕Surface
        """
        # 渲染金币图标（带脉冲效果）
        if self.pulse_effect:
            scaled_image = pygame.transform.scale(
                self.coin_image, 
                (int(self.coin_image.get_width() * self.pulse_scale), 
                 int(self.coin_image.get_height() * self.pulse_scale))
            )
            # 调整位置，使缩放后的图像仍然居中于原位置
            offset_x = (scaled_image.get_width() - self.coin_image.get_width()) // 2
            offset_y = (scaled_image.get_height() - self.coin_image.get_height()) // 2
            screen.blit(scaled_image, (self.position[0] - offset_x, self.position[1] - offset_y))
        else:
            screen.blit(self.coin_image, self.position)
        
        # 渲染金币数量
        coin_text = f"{self.coin_system.coins}"
        self.game.text_renderer.render_text(coin_text, self.text_position, "regular", (255, 255, 255))