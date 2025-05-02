import os
import json

class UpgradeSystem:
    """升级系统类，管理游戏中的各种升级"""
    
    def __init__(self, game):
        """初始化升级系统
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.upgrades = {
            "damage": {
                "name": "伤害升级",
                "description": "增加子弹伤害",
                "max_level": 10,
                "level": 0,
                "base_price": 10,
                "price_increase": 10
            },
            "fire_rate": {
                "name": "射速升级",
                "description": "增加射击速度",
                "max_level": 15,
                "level": 0,
                "base_price": 15,
                "price_increase": 15
            },
            "bullet_speed": {
                "name": "子弹速度升级",
                "description": "增加子弹速度",
                "max_level": 10,
                "level": 0,
                "base_price": 8,
                "price_increase": 8
            }
        }
        
        # 加载保存的升级数据
        self.load_upgrades()
    
    def get_upgrade_level(self, upgrade_type):
        """获取指定升级的等级
        
        Args:
            upgrade_type: 升级类型
        
        Returns:
            当前等级
        """
        if upgrade_type in self.upgrades:
            return self.upgrades[upgrade_type]["level"]
        return 0
    
    def get_upgrade_price(self, upgrade_type):
        """获取指定升级的价格
        
        Args:
            upgrade_type: 升级类型
        
        Returns:
            当前价格
        """
        if upgrade_type not in self.upgrades:
            return 0
        
        upgrade = self.upgrades[upgrade_type]
        level = upgrade["level"]
        
        # 如果已经达到最大等级，返回0（不可购买）
        if level >= upgrade["max_level"]:
            return 0
        
        # 计算当前等级的价格
        return upgrade["base_price"] + level * upgrade["price_increase"]
    
    def purchase_upgrade(self, upgrade_type):
        """购买指定升级
        
        Args:
            upgrade_type: 升级类型
        
        Returns:
            bool: 是否购买成功
        """
        if upgrade_type not in self.upgrades:
            return False
        
        upgrade = self.upgrades[upgrade_type]
        level = upgrade["level"]
        
        # 如果已经达到最大等级，无法购买
        if level >= upgrade["max_level"]:
            return False
        
        # 计算价格
        price = self.get_upgrade_price(upgrade_type)
        
        # 检查金币是否足够
        if self.game.coin_system.coins < price:
            return False
        
        # 扣除金币
        if not self.game.coin_system.spend_coins(price):
            return False
        
        # 升级
        upgrade["level"] += 1
        
        # 保存升级数据
        self.save_upgrades()
        
        # 应用升级效果
        self.apply_upgrades(self.game.player)
        
        return True
    
    def apply_upgrades(self, player):
        """将所有升级效果应用到玩家
        
        Args:
            player: 玩家对象
        """
        # 应用伤害升级
        damage_level = self.get_upgrade_level("damage")
        player.set_bullet_damage(1 + damage_level)
        
        # 应用射速升级
        fire_rate_level = self.get_upgrade_level("fire_rate")
        cooldown = max(0.1, 0.5 - 0.05 * fire_rate_level)  # 最小冷却时间为0.1秒
        player.set_fire_cooldown(cooldown)
        
        # 应用子弹速度升级
        bullet_speed_level = self.get_upgrade_level("bullet_speed")
        player.set_bullet_speed(5 + bullet_speed_level)
    
    def save_upgrades(self):
        """保存升级数据（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，升级数据由SaveManager统一管理
        pass
    
    def load_upgrades(self):
        """加载升级数据（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，升级数据由SaveManager统一管理
        pass
    
    def reset(self):
        """重置所有升级（已禁用，由SaveManager统一管理）"""
        # 此方法已禁用，升级数据由SaveManager统一管理
        pass