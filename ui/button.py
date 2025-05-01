import pygame

from config import *
from core.resource_manager import ResourceManager

class Button(pygame.sprite.Sprite):
    """按钮类，用于游戏菜单"""
    
    def __init__(self, x, y, width, height, text, font_size=40, font_type="regular"):
        """初始化按钮对象
        
        Args:
            x: 按钮的x坐标
            y: 按钮的y坐标
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            font_size: 字体大小
            font_type: 字体类型
        """
        super().__init__()
        self.original_image = ResourceManager.load_image(BUTTON_IMAGE)
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text = text
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.Font(REGULAR_FONT, font_size)
        
        # 鼠标悬停状态
        self.is_hovered = False
        self.original_width = width
        self.original_height = height
        self.hover_scale = 1.03  # 悬停时的放大比例
        self.animation_speed = 0.05  # 动画速度
        self.current_scale = 1.0  # 当前缩放比例
        
        # 颜色变化相关
        self.normal_color = (255, 255, 255)  # 正常状态下的文字颜色
        self.hover_color = (0, 255, 0)  # 悬停状态下的文字颜色
        self.current_color = self.normal_color  # 当前文字颜色
        self.color_transition_speed = 15  # 颜色过渡速度
        
    def update(self):
        """更新按钮状态，处理鼠标悬停动画"""
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        
        # 检测鼠标是否悬停在按钮上
        hover = self.rect.collidepoint(mouse_pos)
        
        # 根据悬停状态调整按钮大小
        if hover and not self.is_hovered:
            self.is_hovered = True
        elif not hover and self.is_hovered:
            self.is_hovered = False
            
        # 平滑动画效果 - 大小变化
        target_scale = self.hover_scale if self.is_hovered else 1.0
        
        if self.current_scale != target_scale:
            # 平滑过渡到目标比例
            if self.current_scale < target_scale:
                self.current_scale = min(self.current_scale + self.animation_speed, target_scale)
            else:
                self.current_scale = max(self.current_scale - self.animation_speed, target_scale)
                
            # 更新按钮图像大小
            new_width = int(self.original_width * self.current_scale)
            new_height = int(self.original_height * self.current_scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            
            # 保持按钮中心位置不变
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # 平滑动画效果 - 颜色变化
        target_color = self.hover_color if self.is_hovered else self.normal_color
        
        # 平滑过渡颜色
        if self.current_color != target_color:
            r, g, b = self.current_color
            tr, tg, tb = target_color
            
            # 计算每个颜色通道的新值
            new_r = self._transition_color_component(r, tr)
            new_g = self._transition_color_component(g, tg)
            new_b = self._transition_color_component(b, tb)
            
            self.current_color = (new_r, new_g, new_b)
    
    def _transition_color_component(self, current, target):
        """平滑过渡单个颜色通道的值
        
        Args:
            current: 当前颜色值
            target: 目标颜色值
            
        Returns:
            int: 过渡后的颜色值
        """
        if current < target:
            return min(current + self.color_transition_speed, target)
        elif current > target:
            return max(current - self.color_transition_speed, target)
        return current
        
    def draw(self, surface):
        """绘制按钮
        
        Args:
            surface: 绘制的目标表面
        """
        # 更新按钮状态
        self.update()
        
        # 绘制按钮背景
        surface.blit(self.image, self.rect)
        
        # 绘制按钮文本
        text_surface = self.font.render(self.text, True, self.current_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        """检测按钮是否被点击
        
        Args:
            pos: 鼠标点击位置
            
        Returns:
            bool: 如果点击返回True，否则返回False
        """
        return self.rect.collidepoint(pos)
