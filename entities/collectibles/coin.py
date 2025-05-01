import pygame
import random
import math

class Coin(pygame.sprite.Sprite):
    """金币类，表示游戏中可收集的金币"""
    
    def __init__(self, x, y, value=1):
        """初始化金币对象
        
        Args:
            x: 金币的x坐标
            y: 金币的y坐标
            value: 金币的价值
        """
        super().__init__()
        
        # 创建金币图像
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (10, 10), 10)  # 金色圆形
        pygame.draw.circle(self.image, (255, 165, 0), (10, 10), 8, 2)  # 橙色边框
        
        # 设置金币属性
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value
        
        # 金币物理属性
        self.velocity_x = random.uniform(-2, 2)  # 随机水平速度
        self.velocity_y = random.uniform(-5, -3)  # 随机向上初速度
        self.gravity = 0.2  # 重力加速度
        self.friction = 0.95  # 摩擦系数
        self.bounce_factor = 0.6  # 弹跳系数
        
        # 金币动画属性
        self.rotation = 0  # 旋转角度
        self.rotation_speed = random.uniform(-5, 5)  # 旋转速度
        self.scale_factor = 1.0  # 缩放因子
        self.scale_direction = 0.02  # 缩放方向和速度
        self.lifetime = 300  # 金币存在的帧数
        self.collected = False  # 是否被收集
        self.collection_target = None  # 收集目标位置
        self.collection_speed = 0  # 收集速度
        
        # 自动收集相关
        self.auto_collect_timer = 30  # 0.5秒后自动收集（假设游戏运行在60FPS）
        self.auto_collect_started = False  # 是否已开始自动收集
        
        # 根据价值设置金币大小和颜色
        if value > 1:
            # 更大的金币
            scale = min(1.5, 1.0 + 0.1 * value)  # 最大1.5倍大小
            self.image = pygame.transform.scale(
                self.image, 
                (int(self.image.get_width() * scale), int(self.image.get_height() * scale))
            )
            self.rect = self.image.get_rect(center=(x, y))
            
            # 更高价值的金币颜色更亮
            if value >= 5:
                # 白金色
                self.original_image = self.image.copy()
                pygame.draw.circle(self.image, (230, 230, 250), (self.image.get_width()//2, self.image.get_height()//2), 
                                  self.image.get_width()//2)
                pygame.draw.circle(self.image, (200, 200, 220), (self.image.get_width()//2, self.image.get_height()//2), 
                                  self.image.get_width()//2 - 2, 2)
    
    def update(self):
        """更新金币状态"""
        if self.collected:
            self._update_collection()
        else:
            self._update_physics()
            
            # 检查是否应该开始自动收集
            if not self.auto_collect_started:
                self.auto_collect_timer -= 1
                if self.auto_collect_timer <= 0:
                    self.auto_collect_started = True
                    self.start_collection()
        
        # 更新动画
        self._update_animation()
        
        # 减少生命周期
        self.lifetime -= 1
        
        # 如果生命周期结束，移除金币
        if self.lifetime <= 0:
            self.kill()
    
    def _update_physics(self):
        """更新金币物理状态"""
        # 应用重力
        self.velocity_y += self.gravity
        
        # 应用摩擦力
        self.velocity_x *= self.friction
        
        # 更新位置
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # 检测地面碰撞（屏幕底部）
        if self.rect.bottom >= 600:  # 假设屏幕高度为600
            self.rect.bottom = 600
            self.velocity_y = -self.velocity_y * self.bounce_factor
            
            # 如果速度很小，停止弹跳
            if abs(self.velocity_y) < 1:
                self.velocity_y = 0
        
        # 检测左右边界碰撞
        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocity_x = -self.velocity_x * self.bounce_factor
        elif self.rect.right >= 1200:  # 假设屏幕宽度为1200
            self.rect.right = 1200
            self.velocity_x = -self.velocity_x * self.bounce_factor
    
    def start_collection(self):
        """开始自动收集金币，让金币飞向玩家"""
        # 获取金币UI的位置
        # 根据CoinDisplay类中的定义，金币图标位置在(50, 40)
        target_position = (50, 40)  # UI中金币图标的位置
        
        # 调用collect方法开始收集动画
        coin_value = self.collect(target_position)
        
        # 增加收集速度，使金币更快地飞向目标
        self.collection_speed = 8  # 从5增加到8，提高初始速度
        
        # 通知游戏增加金币数量
        # 由于我们不能直接访问coin_system，我们需要在Game类中处理
        # 我们将在Game.update方法中检测collected状态的金币
    
    def _update_collection(self):
        """更新金币收集动画"""
        if self.collection_target:
            # 计算到目标的方向向量
            dx = self.collection_target[0] - self.rect.centerx
            dy = self.collection_target[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 如果已经非常接近目标，直接移除
            if distance < 5:
                self.kill()
                return
            
            # 增加收集速度（加速效果）
            self.collection_speed += 0.8  # 从0.5增加到0.8，提高加速度
            max_speed = 30  # 从20增加到30，提高最大速度
            self.collection_speed = min(self.collection_speed, max_speed)
            
            # 计算移动距离
            move_distance = min(distance, self.collection_speed)
            
            # 计算新位置
            if distance > 0:  # 避免除以零
                self.rect.centerx += dx / distance * move_distance
                self.rect.centery += dy / distance * move_distance
    
    def collect(self, target_position):
        """收集金币
        
        Args:
            target_position: 收集目标位置（通常是UI中金币计数器的位置）
        
        Returns:
            int: 金币的价值
        """
        if not self.collected:
            self.collected = True
            self.collection_target = target_position
            self.velocity_x = 0
            self.velocity_y = 0
            self.gravity = 0
            self.lifetime = 120  # 收集动画持续120帧，从60帧增加到120帧
            return self.value
        return 0
        
    def _update_animation(self):
        """更新金币动画效果"""
        # 旋转金币
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360
        
        # 缩放效果（呼吸效果）
        if not self.collected:
            self.scale_factor += self.scale_direction
            if self.scale_factor >= 1.1:
                self.scale_factor = 1.1
                self.scale_direction = -0.02
            elif self.scale_factor <= 0.9:
                self.scale_factor = 0.9
                self.scale_direction = 0.02
        else:
            # 收集时缩小金币，减缓缩放速度
            self.scale_factor *= 0.98  # 从0.95改为0.98，减缓缩放速度
            
    def render(self, screen):
        """渲染金币
        
        Args:
            screen: 游戏屏幕Surface
        """
        # 创建旋转和缩放后的图像
        rotated_image = pygame.transform.rotozoom(self.image, self.rotation, self.scale_factor)
        
        # 如果正在收集，应用淡出效果
        if self.collected:
            # 计算透明度（从255逐渐减小到0）
            alpha = int(255 * (self.lifetime / 120))  # 修改为120帧
            rotated_image.set_alpha(alpha)
        
        # 绘制金币
        screen.blit(rotated_image, rotated_image.get_rect(center=self.rect.center))
        
        # 如果金币价值大于1，显示数值
        if self.value > 1 and not self.collected:
            font = pygame.font.Font(None, 20)
            value_text = font.render(str(self.value), True, (255, 255, 255))
            screen.blit(value_text, (self.rect.centerx - value_text.get_width()//2, 
                                    self.rect.centery - value_text.get_height()//2))