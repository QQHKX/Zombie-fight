import pygame
import random
from entities.zombies.base_zombie import BaseZombie

class TankZombie(BaseZombie):
    """坦克僵尸类，生命值高但速度慢"""
    
    def __init__(self, y, level=1):
        """初始化坦克僵尸
        
        Args:
            y: 僵尸的y坐标
            level: 僵尸等级
        """
        super().__init__(y, level, "tank")
        
        # 坦克僵尸特有属性
        self.description = "坦克僵尸，生命值高但速度慢"
        self.armor = int(10 * (1 + (self.level - 1) * 0.2))  # 护甲值，减少受到的伤害
        self.shield_active = False  # 护盾是否激活
        self.shield_cooldown = 0  # 护盾冷却时间
        self.shield_duration = 0  # 护盾持续时间
        
    def update(self):
        """更新坦克僵尸状态和位置"""
        # 处理护盾逻辑
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
        
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        elif random.random() < 0.01 and not self.shield_active:  # 1%的概率触发护盾
            self.special_ability()
        
        # 调用父类的update方法
        return super().update()
    
    def take_damage(self, damage):
        """受到伤害，坦克僵尸有护甲减伤和护盾减伤
        
        Args:
            damage: 受到的伤害值
            
        Returns:
            bool: 如果僵尸死亡则返回True，否则返回False
        """
        # 如果护盾激活，减少80%伤害
        if self.shield_active:
            damage = damage * 0.4  # 减少60%伤害
         
        
        # 护甲减伤
        actual_damage = max(1, damage - self.armor)  # 至少造成1点伤害
        
        # 调用父类的take_damage方法
        return super().take_damage(actual_damage)
    
    def special_ability(self):
        """坦克僵尸的特殊能力：临时护盾"""
        if self.shield_cooldown <= 0 and not self.shield_active:
            self.shield_active = True
            self.shield_duration = 120  # 护盾持续120帧，约2秒
            self.shield_cooldown = 600  # 护盾冷却600帧，约10秒
    
    def render(self, screen):
        """渲染坦克僵尸
        
        Args:
            screen: 游戏屏幕Surface
        """
        # 调用父类的render方法
        super().render(screen)
        
        # 如果护盾激活，绘制护盾效果
        if self.shield_active:
            # 创建半透明的护盾效果，调整护盾大小为僵尸的0.9倍
            shield_width = int(self.rect.width * 0.9)
            shield_height = int(self.rect.height * 0.9)
            shield_surface = pygame.Surface((shield_width, shield_height), pygame.SRCALPHA)
            
            # 绘制椭圆形护盾，填充蓝紫色半透明效果
            pygame.draw.ellipse(shield_surface, (120, 80, 255, 80), shield_surface.get_rect())
            
            # 绘制护盾边缘，增加一个发光效果
            pygame.draw.ellipse(shield_surface, (150, 120, 255, 120), shield_surface.get_rect(), 2)
            
            # 确保护盾位于僵尸正中心，向左偏移以更好地覆盖僵尸
            shield_rect = shield_surface.get_rect()
            shield_rect.centerx = self.rect.centerx - 35  # 向左偏移15像素
            shield_rect.centery = self.rect.centery - 20  # 向上偏移10像素
            
            # 绘制护盾
            screen.blit(shield_surface, shield_rect)