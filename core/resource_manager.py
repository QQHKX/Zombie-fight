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
            image = pygame.image.load(file_path)
            # 记录日志
            from utils.logger import log_resource
            log_resource("图片加载成功", file_path=file_path)
            return image
        except pygame.error as e:
            
            from utils.logger import log_error
            log_error("图片加载失败", file_path=file_path, error=str(e))
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
            font = pygame.font.Font(file_path, size)
            # 记录日志
            from utils.logger import log_resource
            log_resource("字体加载成功", file_path=file_path, size=size)
            return font
        except pygame.error as e:
            
            from utils.logger import log_error
            log_error("字体加载失败", file_path=file_path, size=size, error=str(e))
            sys.exit(1)
    
    @staticmethod
    def load_sound(file_path):
        """加载音频资源
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            加载的音频对象，如果加载失败则返回None
        """
        if pygame.mixer.get_init():
            try:
                sound = pygame.mixer.Sound(file_path)
                # 记录日志
                from utils.logger import log_resource
                log_resource("音频加载成功", file_path=file_path)
                return sound
            except pygame.error as e:
                
                from utils.logger import log_error
                log_error("音频加载失败", file_path=file_path, error=str(e))
                return None
        return None
    
    @staticmethod
    def init_sound_channels(num_channels=8):
        """初始化多个声道用于同时播放多个音效
        
        Args:
            num_channels: 声道数量，默认为8
            
        Returns:
            声道列表
        """
        if pygame.mixer.get_init():
            pygame.mixer.set_num_channels(num_channels)
            channels = [pygame.mixer.Channel(i) for i in range(num_channels)]
            return channels
        return []