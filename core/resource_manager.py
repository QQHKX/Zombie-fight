import pygame
import sys

class ResourceManager:
    """资源管理类，负责加载和管理游戏资源"""
    
    @staticmethod
    def load_image(file_path):
        """加载图片资源
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            加载的图片对象
            
        Raises:
            pygame.error: 如果图片加载失败
        """
        try:
            return pygame.image.load(file_path)
        except pygame.error as e:
            print(f"无法加载图片: {file_path}")
            print(f"错误信息: {e}")
            sys.exit(1)
    
    @staticmethod
    def load_font(file_path, size):
        """加载字体资源
        
        Args:
            file_path: 字体文件路径
            size: 字体大小
            
        Returns:
            加载的字体对象
            
        Raises:
            pygame.error: 如果字体加载失败
        """
        try:
            return pygame.font.Font(file_path, size)
        except pygame.error as e:
            print(f"无法加载字体: {file_path}")
            print(f"错误信息: {e}")
            sys.exit(1)
    
    @staticmethod
    def load_sound(file_path):
        """加载音频资源
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            加载的音频对象
            
        Raises:
            pygame.error: 如果音频加载失败
        """
        try:
            return pygame.mixer.Sound(file_path)
        except pygame.error as e:
            print(f"无法加载音频: {file_path}")
            print(f"错误信息: {e}")
            return None