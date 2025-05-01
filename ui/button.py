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
        
    def draw(self, surface):
        """绘制按钮
        
        Args:
            surface: 绘制的目标表面
        """
        # 绘制按钮背景
        surface.blit(self.image, self.rect)
        
        # 绘制按钮文本
        text_surface = self.font.render(self.text, True, (0, 0, 0))
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
