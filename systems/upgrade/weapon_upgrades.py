import pygame
from entities.bullet import Bullet

class WeaponUpgrades:
    """武器升级类，管理武器升级效果"""
    
    def __init__(self, upgrade_system):
        """初始化武器升级类
        
        Args:
            upgrade_system: 升级系统实例
        """
        self.upgrade_system = upgrade_system
    
    def apply_damage_upgrade(self, bullet, level):
        """应用伤害升级效果
        
        Args:
            bullet: 子弹对象
            level: 升级等级
        """
        # 每级增加1点伤害
        bullet.damage = 1 + level
        return bullet
    
    def apply_fire_rate_upgrade(self, player, level):
        """应用射速升级效果
        
        Args:
            player: 玩家对象
            level: 升级等级
        """
        # 基础冷却时间为0.5秒，每级减少0.05秒，最低0.1秒
        cooldown = max(0.1, 0.5 - 0.05 * level)
        player.set_fire_cooldown(cooldown)
        return player
    
    def apply_bullet_speed_upgrade(self, bullet, level):
        """应用子弹速度升级效果
        
        Args:
            bullet: 子弹对象
            level: 升级等级
        """
        # 基础速度为5，每级增加1点速度
        bullet.speed = 5 + level
        return bullet
    
    def create_upgraded_bullet(self, x, y, target_y):
        """创建已应用所有升级效果的子弹
        
        Args:
            x: 子弹的初始x坐标
            y: 子弹的初始y坐标
            target_y: 子弹的目标y坐标
        
        Returns:
            升级后的子弹对象
        """
        # 获取升级等级
        damage_level = self.upgrade_system.get_upgrade_level("damage")
        speed_level = self.upgrade_system.get_upgrade_level("bullet_speed")
        
        # 计算升级后的属性
        damage = 1 + damage_level
        speed = 5 + speed_level
        
        # 创建子弹
        bullet = Bullet(x, y, target_y, speed, damage)
        
        # 记录日志
        from utils.logger import log_upgrade
        log_upgrade("创建升级子弹", damage=damage, speed=speed, position=(x, y))
        
        return bullet
    
    def get_upgrade_description(self, upgrade_type, level):
        """获取升级的详细描述
        
        Args:
            upgrade_type: 升级类型
            level: 当前等级
        
        Returns:
            描述文本
        """
        if upgrade_type == "damage":
            return f"伤害: {1 + level} (+1)"
        elif upgrade_type == "fire_rate":
            cooldown = max(0.1, 0.5 - 0.05 * level)
            next_cooldown = max(0.1, 0.5 - 0.05 * (level + 1))
            return f"射速: {1/cooldown:.1f}发/秒 → {1/next_cooldown:.1f}发/秒"
        elif upgrade_type == "bullet_speed":
            return f"子弹速度: {5 + level} (+1)"
        return ""
    
    def render_upgrade_preview(self, screen, upgrade_type, level, position):
        """渲染升级预览效果
        
        Args:
            screen: 游戏屏幕
            upgrade_type: 升级类型
            level: 当前等级
            position: 渲染位置
        """
        # 根据升级类型绘制不同的预览
        if upgrade_type == "damage":
            # 绘制伤害预览
            pygame.draw.circle(screen, (255, 0, 0), position, 10 + level * 2)
        elif upgrade_type == "fire_rate":
            # 绘制射速预览
            cooldown = max(0.1, 0.5 - 0.05 * level)
            for i in range(int(1/cooldown)):
                pygame.draw.circle(screen, (0, 255, 0), 
                                  (position[0] - 20 + i * 10, position[1]), 5)
        elif upgrade_type == "bullet_speed":
            # 绘制子弹速度预览
            pygame.draw.rect(screen, (0, 0, 255), 
                            (position[0] - 15, position[1] - 5, 
                             10 + level * 5, 10))