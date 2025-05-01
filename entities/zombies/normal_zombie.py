import pygame
from entities.zombies.base_zombie import BaseZombie

class NormalZombie(BaseZombie):
    """普通僵尸类，基本僵尸类型，属性平衡"""
    
    def __init__(self, y, level=1):
        """初始化普通僵尸
        
        Args:
            y: 僵尸的y坐标
            level: 僵尸等级
        """
        super().__init__(y, level, "normal")
        
        # 普通僵尸特有属性
        self.description = "普通僵尸，基本属性平衡"
        
    def special_ability(self):
        """普通僵尸的特殊能力（暂无）"""
        # 普通僵尸没有特殊能力
        pass