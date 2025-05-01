import random
import time

from entities.zombies.normal_zombie import NormalZombie
from entities.zombies.fast_zombie import FastZombie
from entities.zombies.tank_zombie import TankZombie
from config import *

class ZombieSpawner:
    """僵尸生成系统，负责生成不同类型和等级的僵尸"""
    
    def __init__(self, game):
        """初始化僵尸生成器
        
        Args:
            game: 游戏主类实例
        """
        self.game = game
        self.start_time = time.time()
        self.last_spawn_time = time.time()
        self.wave_start_time = time.time()
        self.current_wave = 1
        self.wave_duration = 30  # 每波持续30秒
        self.wave_break_duration = 5  # 波次间隔5秒
        self.in_wave_break = False
        self.wave_break_start_time = 0
        
        # 僵尸生成配置
        self.base_spawn_interval = 2.0  # 基础生成间隔（秒）
        self.min_spawn_interval = 0.5  # 最小生成间隔（秒）
        self.max_zombies_per_spawn = 1  # 每次生成的最大僵尸数量
        
        # 僵尸类型权重（初始值）
        self.zombie_weights = {
            "normal": 100,
            "fast": 0,
            "tank": 0
        }
        
        # 僵尸等级概率（初始值）
        self.level_probabilities = {
            1: 100,  # 1级僵尸概率100%
            2: 0,    # 2级僵尸概率0%
            3: 0,    # 3级僵尸概率0%
            4: 0,    # 4级僵尸概率0%
            5: 0     # 5级僵尸概率0%
        }
    
    def update(self):
        """更新僵尸生成器状态"""
        current_time = time.time()
        game_time = current_time - self.start_time
        
        # 处理波次逻辑
        if self.in_wave_break:
            # 检查休息时间是否结束
            if current_time - self.wave_break_start_time >= self.wave_break_duration:
                self.in_wave_break = False
                self.wave_start_time = current_time
                self.current_wave += 1
                print(f"第 {self.current_wave} 波僵尸来袭！")
        else:
            # 检查当前波次是否结束
            wave_elapsed = current_time - self.wave_start_time
            if wave_elapsed >= self.wave_duration:
                self.in_wave_break = True
                self.wave_break_start_time = current_time
                print(f"第 {self.current_wave} 波结束，准备下一波...")
        
        # 如果在波次休息中，不生成僵尸
        if self.in_wave_break:
            return
        
        # 更新僵尸类型权重和等级概率
        self._update_zombie_weights(game_time)
        self._update_level_probabilities(game_time)
        
        # 计算当前生成间隔
        spawn_interval = max(self.min_spawn_interval, 
                            self.base_spawn_interval - (game_time / 300) * 1.5)  # 每5分钟减少1.5秒，最小0.5秒
        
        # 计算每次生成的僵尸数量
        zombies_per_spawn = min(5, 1 + int(game_time // 180))  # 每3分钟增加1个，最多5个
        
        # 检查是否应该生成僵尸
        if current_time - self.last_spawn_time >= spawn_interval:
            self.last_spawn_time = current_time
            self._spawn_zombies(zombies_per_spawn)
    
    def _update_zombie_weights(self, game_time):
        """根据游戏时间更新僵尸类型权重
        
        Args:
            game_time: 游戏进行的时间（秒）
        """
        # 随着时间推移，增加快速僵尸和坦克僵尸的权重
        minutes = game_time / 60
        
        # 2分钟后开始出现快速僵尸
        if minutes >= 2:
            fast_weight = min(50, int((minutes - 2) * 10))  # 每分钟增加10点权重，最高50
            self.zombie_weights["fast"] = fast_weight
        
        # 5分钟后开始出现坦克僵尸
        if minutes >= 5:
            tank_weight = min(30, int((minutes - 5) * 6))  # 每分钟增加6点权重，最高30
            self.zombie_weights["tank"] = tank_weight
    
    def _update_level_probabilities(self, game_time):
        """根据游戏时间更新僵尸等级概率
        
        Args:
            game_time: 游戏进行的时间（秒）
        """
        minutes = game_time / 60
        
        # 重置所有概率
        for level in self.level_probabilities:
            self.level_probabilities[level] = 0
        
        # 根据游戏时间设置不同等级的概率
        if minutes < 3:
            # 3分钟内只有1级僵尸
            self.level_probabilities[1] = 100
        elif minutes < 6:
            # 3-6分钟有1-2级僵尸
            self.level_probabilities[1] = 80
            self.level_probabilities[2] = 20
        elif minutes < 10:
            # 6-10分钟有1-3级僵尸
            self.level_probabilities[1] = 60
            self.level_probabilities[2] = 30
            self.level_probabilities[3] = 10
        elif minutes < 15:
            # 10-15分钟有1-4级僵尸
            self.level_probabilities[1] = 40
            self.level_probabilities[2] = 30
            self.level_probabilities[3] = 20
            self.level_probabilities[4] = 10
        else:
            # 15分钟后有1-5级僵尸
            self.level_probabilities[1] = 30
            self.level_probabilities[2] = 25
            self.level_probabilities[3] = 20
            self.level_probabilities[4] = 15
            self.level_probabilities[5] = 10
    
    def _spawn_zombies(self, count):
        """生成指定数量的僵尸
        
        Args:
            count: 要生成的僵尸数量
        """
        for _ in range(count):
            # 随机选择僵尸类型
            zombie_type = self._select_zombie_type()
            
            # 随机选择僵尸等级
            zombie_level = self._select_zombie_level()
            
            # 随机选择僵尸y坐标
            y = random.randint(50, SCREEN_HEIGHT - 230)
            
            # 根据类型创建僵尸
            zombie = None
            if zombie_type == "normal":
                zombie = NormalZombie(y, zombie_level)
            elif zombie_type == "fast":
                zombie = FastZombie(y, zombie_level)
            elif zombie_type == "tank":
                zombie = TankZombie(y, zombie_level)
            
            # 将僵尸添加到游戏中
            if zombie:
                self.game.zombies.add(zombie)
                self.game.all_sprites.add(zombie)
    
    def _select_zombie_type(self):
        """根据权重随机选择僵尸类型
        
        Returns:
            str: 选择的僵尸类型
        """
        total_weight = sum(self.zombie_weights.values())
        r = random.randint(1, total_weight)
        
        cumulative_weight = 0
        for zombie_type, weight in self.zombie_weights.items():
            cumulative_weight += weight
            if r <= cumulative_weight:
                return zombie_type
        
        # 默认返回普通僵尸
        return "normal"
    
    def _select_zombie_level(self):
        """根据概率随机选择僵尸等级
        
        Returns:
            int: 选择的僵尸等级
        """
        total_prob = sum(self.level_probabilities.values())
        r = random.randint(1, total_prob)
        
        cumulative_prob = 0
        for level, prob in self.level_probabilities.items():
            cumulative_prob += prob
            if r <= cumulative_prob:
                return level
        
        # 默认返回1级
        return 1
    
    def get_wave_info(self):
        """获取当前波次信息
        
        Returns:
            dict: 包含波次信息的字典
        """
        current_time = time.time()
        
        if self.in_wave_break:
            # 计算休息剩余时间
            remaining = self.wave_break_duration - (current_time - self.wave_break_start_time)
            return {
                "wave": self.current_wave,
                "state": "break",
                "remaining": max(0, remaining)
            }
        else:
            # 计算当前波次剩余时间
            remaining = self.wave_duration - (current_time - self.wave_start_time)
            return {
                "wave": self.current_wave,
                "state": "active",
                "remaining": max(0, remaining)
            }
    
    def reset(self):
        """重置僵尸生成器状态"""
        self.start_time = time.time()
        self.last_spawn_time = time.time()
        self.wave_start_time = time.time()
        self.current_wave = 1
        self.in_wave_break = False
        
        # 重置僵尸类型权重
        self.zombie_weights = {
            "normal": 100,
            "fast": 0,
            "tank": 0
        }
        
        # 重置僵尸等级概率
        self.level_probabilities = {
            1: 100,
            2: 0,
            3: 0,
            4: 0,
            5: 0
        }