import os
import json

class SaveManager:
    """存档管理系统，统一管理游戏存档数据"""
    
    def __init__(self, game):
        """初始化存档管理系统
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
        
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 存档数据默认值
        self.default_save_data = {
            "coins": 30,  # 初始金币数
            "upgrades": {},  # 升级信息
            "completed_levels": [],  # 已通关关卡
            "current_level": 1,  # 当前关卡
            "highest_score": 0  # 最高分数
        }
        
        # 当前存档数据
        self.save_data = self.default_save_data.copy()
        
        # 加载存档数据
        self.load_save_data()
    
    def save_game(self):
        """保存游戏数据（仅在通关后调用）"""
        # 更新存档数据
        self.save_data["coins"] = self.game.coin_system.coins
        
        # 保存升级数据
        self.save_data["upgrades"] = {}
        for upgrade_type, upgrade in self.game.upgrade_system.upgrades.items():
            self.save_data["upgrades"][upgrade_type] = upgrade["level"]
        
        # 保存到文件
        save_path = os.path.join(self.save_dir, "save_data.json")
        try:
            with open(save_path, "w") as f:
                json.dump(self.save_data, f)
            print("游戏数据保存成功")
        except Exception as e:
            print(f"保存游戏数据失败: {e}")
    
    def load_save_data(self):
        """加载存档数据"""
        save_path = os.path.join(self.save_dir, "save_data.json")
        
        # 如果保存文件存在，加载数据
        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as f:
                    loaded_data = json.load(f)
                    # 将加载的数据合并到save_data中
                    for key, value in loaded_data.items():
                        self.save_data[key] = value
                print("游戏数据加载成功")
            except Exception as e:
                print(f"加载游戏数据失败: {e}")
                # 加载失败时使用默认数据
                self.save_data = self.default_save_data.copy()
        else:
            print("未找到存档文件，使用默认数据")
    
    def apply_save_data(self):
        """应用存档数据到游戏（游戏启动时调用）"""
        # 应用金币数据
        self.game.coin_system.coins = self.save_data.get("coins", 30)
        
        # 应用升级数据
        upgrades_data = self.save_data.get("upgrades", {})
        for upgrade_type, level in upgrades_data.items():
            if upgrade_type in self.game.upgrade_system.upgrades:
                self.game.upgrade_system.upgrades[upgrade_type]["level"] = level
        
        # 应用升级效果
        if hasattr(self.game, 'player') and self.game.player is not None:
            self.game.upgrade_system.apply_upgrades(self.game.player)
        
        # 禁用其他系统的自动保存功能
        self.disable_auto_save()
    
    def disable_auto_save(self):
        """禁用其他系统的自动保存功能"""
        # 重写金币系统的save_coins方法
        original_save_coins = self.game.coin_system.save_coins
        self.game.coin_system.save_coins = lambda: None
        
        # 重写升级系统的save_upgrades方法
        original_save_upgrades = self.game.upgrade_system.save_upgrades
        self.game.upgrade_system.save_upgrades = lambda: None
        
        # 重写金币系统的reset方法，确保不会重置为0
        original_reset = self.game.coin_system.reset
        self.game.coin_system.reset = lambda: None
    
    def complete_level(self, level_id, score):
        """完成关卡
        
        Args:
            level_id: 关卡ID
            score: 得分
        """
        # 更新已完成关卡列表
        if level_id not in self.save_data["completed_levels"]:
            self.save_data["completed_levels"].append(level_id)
        
        # 更新最高分
        if score > self.save_data["highest_score"]:
            self.save_data["highest_score"] = score
        
        # 更新当前关卡（解锁下一关）
        if level_id == self.save_data["current_level"]:
            self.save_data["current_level"] = level_id + 1
        
        # 保存游戏数据
        self.save_game()
    
    def get_completed_levels(self):
        """获取已完成关卡列表
        
        Returns:
            list: 已完成关卡ID列表
        """
        return self.save_data["completed_levels"]
    
    def get_current_level(self):
        """获取当前关卡
        
        Returns:
            int: 当前关卡ID
        """
        return self.save_data["current_level"]
    
    def get_highest_score(self):
        """获取最高分数
        
        Returns:
            int: 最高分数
        """
        return self.save_data["highest_score"]
    
    def reset_save_data(self):
        """重置存档数据"""
        self.save_data = self.default_save_data.copy()
        
        # 保存重置后的数据
        self.save_game()
        
        # 重置游戏系统
        self.game.coin_system.reset()
        self.game.upgrade_system.reset()