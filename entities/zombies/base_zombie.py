import pygame
import os
import random

from config import *
from core.resource_manager import ResourceManager

class BaseZombie(pygame.sprite.Sprite):
    """僵尸基类，定义所有僵尸的基本属性和行为"""
    
    # 类变量，所有实例共享
    move_frames_normal = None
    move_frames_fast = None
    move_frames_tank = None
    
    @classmethod
    def preload_animations(cls):
        """预加载所有僵尸动画，游戏启动时调用一次"""
        if cls.move_frames_normal is None:
            cls.move_frames_normal = []
            cls.move_frames_fast = []
            cls.move_frames_tank = []
            
            for i in range(1, 14):
                frame_path = os.path.join(ZOMBIE_MOVE_DIR, f"zombie_move_{i:02d}.png")
                frame = ResourceManager.load_image(frame_path)
                
                cls.move_frames_normal.append(frame)
                
                # 快速僵尸偏绿色
                colorized = frame.copy()
                colorized.fill((100, 255, 100), special_flags=pygame.BLEND_RGB_MULT)
                cls.move_frames_fast.append(colorized)
                
                # 坦克僵尸偏红色
                colorized = frame.copy()
                colorized.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                cls.move_frames_tank.append(colorized)
    
    def __init__(self, y, level=1, zombie_type="normal"):
        """初始化僵尸对象
        
        Args:
            y: 僵尸的y坐标
            level: 僵尸等级，影响生命值和伤害
            zombie_type: 僵尸类型，可以是"normal"、"fast"或"tank"
        """
        super().__init__()
        
        # 僵尸基本属性
        self.level = level
        self.zombie_type = zombie_type
        self.rect = pygame.Rect(SCREEN_WIDTH, y, 180, 180)
        
        # 创建一个比视觉大小小一些的碰撞区域
        self.hit_rect = pygame.Rect(0, 0, 140, 160)
        self.update_hit_rect()  # 初始化碰撞区域位置
        
        # 僵尸状态
        self.state = ZOMBIE_MOVE
        self.animation_index = 0
        
        # 根据僵尸类型和等级设置属性
        self._set_attributes()
        
        # 加载僵尸动画帧
        self.move_frames = self._load_animation_frames()
        
        # 当前显示的帧
        self.image = self.move_frames[0]
        
        # 血条相关
        self.show_health_bar = True
        self.health_bar_width = 50
        self.health_bar_height = 8
        self.health_bar_offset = 10  # 血条距离僵尸顶部的距离
        
        # 掉落金币相关
        self.coin_value = self._calculate_coin_value()
    
    def _set_attributes(self):
        """根据僵尸类型和等级设置属性"""
        # 基础属性（普通僵尸1级）
        base_health = 5
        base_speed = 1
        base_damage = 10
        
        # 根据类型调整基础属性
        if self.zombie_type == "fast":
            base_health *= 0.7  # 快速僵尸生命值较低
            base_speed *= 1.8   # 快速僵尸速度较快
            base_damage *= 0.8  # 快速僵尸伤害较低
        elif self.zombie_type == "tank":
            base_health *= 2.0   # 坦克僵尸生命值较高
            base_speed *= 0.6    # 坦克僵尸速度较慢
            base_damage *= 1.5   # 坦克僵尸伤害较高
        
        # 根据等级提升属性（每级提升20%）
        level_multiplier = 1 + (self.level - 1) * 0.2
        
        # 设置最终属性
        self.max_health = max(1, int(base_health * level_multiplier))  # 确保最小生命值为1
        self.health = self.max_health
        self.speed = base_speed * level_multiplier
        self.damage = int(base_damage * level_multiplier)
    
    def _load_animation_frames(self):
        """获取僵尸动画帧（不再重新加载图片）"""
        # 确保动画已预加载
        if BaseZombie.move_frames_normal is None:
            BaseZombie.preload_animations()
            
        # 根据僵尸类型返回对应的动画帧
        if self.zombie_type == "fast":
            return BaseZombie.move_frames_fast
        elif self.zombie_type == "tank":
            return BaseZombie.move_frames_tank
        else:
            return BaseZombie.move_frames_normal
    
    def _calculate_coin_value(self):
        """计算僵尸掉落的金币价值"""
        # 基础金币价值
        base_value = 1
        
        # 根据类型调整
        if self.zombie_type == "fast":
            base_value = 2
        elif self.zombie_type == "tank":
            base_value = 3
        
        # 根据等级增加（每级增加1）
        return base_value + (self.level - 1)
    
    def update(self):
        """更新僵尸状态和位置"""
        # 更新动画帧，动画速度与移动速度成正比
        if self.state == ZOMBIE_MOVE:
            # 根据移动速度调整动画速度
            animation_speed_factor = max(1, self.speed) / 2.31
            
            # 计算当前应该显示的帧
            frame_index = int(self.animation_index * animation_speed_factor) % len(self.move_frames)
            self.image = self.move_frames[frame_index]
            
            # 更新位置
            self.rect.x -= self.speed
            # 更新碰撞区域位置
            self.update_hit_rect()
        
        self.animation_index += 1
        
        # 如果僵尸到达屏幕左边缘，返回True表示游戏结束
        if self.rect.right <= 0:
            return True
        return False
    
    def update_hit_rect(self):
        """更新碰撞区域的位置，使其跟随僵尸的位置"""
        # 将碰撞区域居中于僵尸的矩形区域
        self.hit_rect.centerx = self.rect.centerx
        self.hit_rect.centery = self.rect.centery
    
    def get_hit_rect(self):
        """获取用于碰撞检测的矩形区域"""
        return self.hit_rect
    
    def take_damage(self, damage):
        """受到伤害
        
        Args:
            damage: 受到的伤害值
            
        Returns:
            bool: 如果僵尸死亡则返回True，否则返回False
        """
        self.health -= damage
        if self.health <= 0:
            return True
        return False
    
    def render_health_bar(self, screen):
        """渲染僵尸血条
        
        Args:
            screen: 游戏屏幕Surface
        """
        if not self.show_health_bar:
            return
        
       # 计算血条位置 - 调整x位置使其更好地对齐僵尸视觉中心
        bar_x = self.rect.centerx - self.health_bar_width // 2 - 50  # 向左偏移20像素
        bar_y = self.rect.top - self.health_bar_offset
        
        # 绘制血条背景
        pygame.draw.rect(screen, (100, 100, 100), 
                        (bar_x, bar_y, self.health_bar_width, self.health_bar_height))
        
        # 计算血量比例
        if self.max_health > 0:  # 防止除以零错误
            health_ratio = max(0, min(1, self.health / self.max_health))  # 确保比例在0-1之间
        else:
            health_ratio = 0
        
        # 根据血量比例确定血条颜色
        if health_ratio > 0.6:
            color = (0, 255, 0)  # 绿色
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # 黄色
        else:
            color = (255, 0, 0)  # 红色
        
        # 绘制血条
        if health_ratio > 0:
            pygame.draw.rect(screen, color, 
                            (bar_x, bar_y, 
                            int(self.health_bar_width * health_ratio), 
                            self.health_bar_height))
        
        # 绘制僵尸等级
        if self.level > 1:
            font = pygame.font.Font(None, 20)
            level_text = font.render(f"Lv.{self.level}", True, (255, 255, 255))
            screen.blit(level_text, (bar_x + self.health_bar_width + 5, bar_y))
    
    def render(self, screen):
        """渲染僵尸
        
        Args:
            screen: 游戏屏幕Surface
        """
        # 绘制僵尸图像
        screen.blit(self.image, self.rect)
        
        # 绘制血条
        self.render_health_bar(screen)
        
        # 调试模式：绘制碰撞区域
        # pygame.draw.rect(screen, (255, 0, 0), self.hit_rect, 2)