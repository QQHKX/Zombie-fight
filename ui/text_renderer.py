import pygame

from config import *
from core.resource_manager import ResourceManager

class TextRenderer:
    """文本渲染类，负责在屏幕上渲染各种文本"""
    
    def __init__(self, canvas):
        """初始化文本渲染器
        
        Args:
            canvas: 游戏画布对象
        """
        self.canvas = canvas
        self.fonts = {
            "regular": ResourceManager.load_font(REGULAR_FONT, 50),
            "warning": ResourceManager.load_font(WARNING_FONT, 80),
            "game_over": ResourceManager.load_font(GAME_OVER_FONT, 100)
        }
    
    def render_text(self, text, position, font_type="regular", color=(0, 0, 0)):
        """渲染文本到画布上
        
        Args:
            text: 要渲染的文本内容
            position: 文本位置，(x, y)元组
            font_type: 字体类型，可选值为"regular", "warning", "game_over"
            color: 文本颜色，RGB元组
        """
        if font_type not in self.fonts:
            font_type = "regular"
            
        text_surface = self.fonts[font_type].render(text, True, color)
        self.canvas.blit(text_surface, position)

