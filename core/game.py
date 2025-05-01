import pygame
import sys
import time
import random
import os
from pygame.locals import *

from config import *
from core.resource_manager import ResourceManager
from entities.player import Player
from entities.zombie import Zombie
from entities.bullet import Bullet
from entities.particle import Particle
from ui.text_renderer import TextRenderer
from ui.button import Button

# 导入新系统
from systems.economy.coin_system import CoinSystem
from ui.hud.coin_display import CoinDisplay
from systems.spawner.zombie_spawner import ZombieSpawner
from systems.upgrade.upgrade_system import UpgradeSystem
from systems.upgrade.weapon_upgrades import WeaponUpgrades
from ui.screens.upgrade_menu import UpgradeMenu
from entities.collectibles.coin import Coin
from entities.zombies.normal_zombie import NormalZombie
from entities.zombies.fast_zombie import FastZombie
from entities.zombies.tank_zombie import TankZombie

class Game:
    """游戏主类，管理游戏状态和逻辑"""
    
    def __init__(self):
        """初始化游戏"""
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()  # 初始化音频系统
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("炮打僵尸_无尽版")
        
        # 加载游戏资源
        self.background_playing = ResourceManager.load_image(BACKGROUND_PLAYING_IMAGE)
        self.background_start_menu = ResourceManager.load_image(BACKGROUND_START_MENU_IMAGE)
        self.game_over_bg = ResourceManager.load_image(GAME_OVER_IMAGE)
        
        # 加载音效
        self.sounds = {
            "bullet_fired": ResourceManager.load_sound(BULLET_FIRED_SOUND),
            "hit": ResourceManager.load_sound(HIT_SOUND)
        }
        
        # 设置打击音效音量
        if self.sounds["hit"]:
            self.sounds["hit"].set_volume(0.3)  # 设置为30%的音量
        
        # 创建文本渲染器
        self.text_renderer = TextRenderer(self.screen)
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()  # 添加粒子效果组
        self.coins = pygame.sprite.Group()  # 添加金币组
        
        # 创建按钮
        self.start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 80, "开始游戏")
        self.quit_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 80, "退出游戏")
        self.resume_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 80, "继续游戏")
        self.restart_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 80, "重新开始")
        self.menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 300, 80, "返回菜单")
        self.upgrade_button = Button(SCREEN_WIDTH - 150, 30, 120, 50, "升级")
        self.pause_button = Button(SCREEN_WIDTH - 150, 90, 120, 50, "暂停")  # 添加暂停按钮
        
        # 创建玩家
        self.player = None
        
        # 初始化新系统
        self.coin_system = CoinSystem(self)
        self.coin_display = CoinDisplay(self, self.coin_system)
        self.zombie_spawner = ZombieSpawner(self)
        self.upgrade_system = UpgradeSystem(self)
        self.weapon_upgrades = WeaponUpgrades(self.upgrade_system)
        self.upgrade_menu = UpgradeMenu(self)
        
        # 添加存档管理系统
        from systems.save_manager import SaveManager
        self.save_manager = SaveManager(self)
        
        # 应用存档数据
        self.save_manager.apply_save_data()
        
        # 游戏状态
        self.game_state = GAME_STATE_START_MENU
        self.start_time = 0
        self.zombie_spawn_timer = 0
        self.clock = pygame.time.Clock()
        
        # 鼠标左键按下状态跟踪
        self.mouse_left_down = False
        self.last_mouse_pos = (0, 0)
        
        # 加载背景音乐
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)  # 循环播放
        except pygame.error as e:
            print(f"无法加载背景音乐: {e}")

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            # 退出事件
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.quit_game()
            
            # 如果升级菜单激活，优先处理升级菜单事件
            if self.upgrade_menu.active:
                if self.upgrade_menu.handle_event(event):
                    return
            
            # 鼠标按下事件
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                self.last_mouse_pos = mouse_pos
                
                # 开始菜单状态
                if self.game_state == GAME_STATE_START_MENU:
                    if self.start_button.is_clicked(mouse_pos):
                        self.start_game()
                    elif self.quit_button.is_clicked(mouse_pos):
                        self.quit_game()
                
                # 游戏进行状态
                elif self.game_state == GAME_STATE_PLAYING:
                    # 检查是否点击了升级按钮
                    if self.upgrade_button.is_clicked(mouse_pos):
                        self.upgrade_menu.show()
                    # 检查是否点击了暂停按钮
                    elif self.pause_button.is_clicked(mouse_pos):
                        self.pause_game()
                    else:
                        # 设置鼠标左键按下状态
                        self.mouse_left_down = True
                        # 立即发射一次子弹
                        self.fire_bullet(mouse_pos[1])
                
                # 游戏暂停状态
                elif self.game_state == GAME_STATE_PAUSED:
                    if self.resume_button.is_clicked(mouse_pos):
                        self.resume_game()
                    elif self.restart_button.is_clicked(mouse_pos):
                        self.reset_game()
                    elif self.menu_button.is_clicked(mouse_pos):
                        self.return_to_menu()
                
                # 游戏结束状态
                elif self.game_state == GAME_STATE_GAME_OVER:
                    if self.restart_button.is_clicked(mouse_pos):
                        self.reset_game()
                    elif self.menu_button.is_clicked(mouse_pos):
                        self.return_to_menu()
            
            # 鼠标释放事件
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                # 重置鼠标左键按下状态
                self.mouse_left_down = False
            
            # 鼠标移动事件 - 允许炮台在发射动画状态时也能移动，包括水平和垂直方向
            elif event.type == MOUSEMOTION and self.game_state == GAME_STATE_PLAYING:
                self.last_mouse_pos = event.pos
                self.player.update(event.pos[1], event.pos[0])
            
            # 暂停/继续游戏
            elif event.type == KEYDOWN and event.key == K_p and self.game_state == GAME_STATE_PLAYING:
                self.pause_game()

    def start_game(self):
        """开始新游戏"""
        # 清空所有精灵组
        self.all_sprites.empty()
        self.zombies.empty()
        self.bullets.empty()
        self.coins.empty()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 重置系统
        self.coin_system.reset()
        self.zombie_spawner.reset()
        self.upgrade_system.reset()
        
        # 应用升级效果到玩家
        self.upgrade_system.apply_upgrades(self.player)
        
        # 设置游戏状态
        self.game_state = GAME_STATE_PLAYING
        self.start_time = time.time()
        self.zombie_spawn_timer = time.time()
    
    def pause_game(self):
        """暂停游戏"""
        self.game_state = GAME_STATE_PAUSED
        pygame.mixer.music.pause()
    
    def resume_game(self):
        """继续游戏"""
        self.game_state = GAME_STATE_PLAYING
        pygame.mixer.music.unpause()
    
    def return_to_menu(self):
        """返回主菜单"""
        self.game_state = GAME_STATE_START_MENU
    
    def reset_game(self):
        """重置游戏状态"""
        # 清空所有精灵组
        self.all_sprites.empty()
        self.zombies.empty()
        self.bullets.empty()
        self.particles.empty()
        self.coins.empty()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 重置游戏状态
        self.score = 0
        self.wave = 1
        self.wave_zombies_count = INITIAL_WAVE_ZOMBIES
        self.zombies_spawned = 0
        self.wave_completed = False
        self.wave_cooldown = 0
        self.game_over = False
        
        # 应用存档数据
        self.save_manager.apply_save_data()
        
        # 重置僵尸生成器
        self.zombie_spawner.reset()
        
        # 重置开始时间
        self.start_time = pygame.time.get_ticks()
        self.zombie_spawn_timer = time.time()
        
        # 重新播放背景音乐
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
    
    def fire_bullet(self, y_pos):
        """发射子弹
        
        Args:
            y_pos: 鼠标的y坐标
        """
        # 检查玩家是否可以发射（冷却时间）
        if not self.player.can_fire():
            return
        
        # 使用武器升级系统创建升级后的子弹
        bullet = self.weapon_upgrades.create_upgraded_bullet(
            self.player.rect.right, y_pos - 40, y_pos
        )
        
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)
        
        # 触发炮台发射动画
        self.player.fire()
        
        # 播放发射音效
        if self.sounds["bullet_fired"]:
            self.sounds["bullet_fired"].play()
            
    def create_hit_particles(self, position):
        """创建打击粒子效果
        
        Args:
            position: 粒子生成位置 (x, y)
        """
        # 创建多个不同颜色、大小和速度的粒子
        colors = [(255, 255, 0), (255, 165, 0), (255, 69, 0), (255, 0, 0)]
        
        for _ in range(15):  # 创建15个粒子
            # 随机选择颜色
            color = random.choice(colors)
            # 随机大小
            size = random.randint(3, 8)
            # 随机速度和方向
            speed_x = random.uniform(-3, 3)
            speed_y = random.uniform(-3, 3)
            # 随机生命周期
            lifetime = random.randint(15, 30)
            
            # 创建粒子并添加到粒子组
            particle = Particle(
                position[0], position[1],
                color=color,
                size=size,
                speed_x=speed_x,
                speed_y=speed_y,
                lifetime=lifetime
            )
            self.particles.add(particle)
    
    def spawn_zombies(self):
        """生成僵尸"""
        # 使用僵尸生成系统生成僵尸
        self.zombie_spawner.update()

    def check_collisions(self):
        """检测碰撞"""
        # 检测子弹和僵尸的碰撞
        for bullet in self.bullets:
            # 使用自定义碰撞检测，检查子弹是否与任何僵尸的hit_rect相交
            for zombie in self.zombies:
                if bullet.rect.colliderect(zombie.get_hit_rect()):
                    # 获取僵尸位置，用于显示得分动画和粒子效果
                    hit_pos = (bullet.rect.centerx, bullet.rect.centery)
                    
                    # 播放打击音效
                    if self.sounds["hit"]:
                        self.sounds["hit"].play()
                    
                    # 创建打击粒子效果
                    self.create_hit_particles(hit_pos)
                    
                    # 对僵尸造成伤害
                    if zombie.take_damage(bullet.damage):
                        # 僵尸死亡，生成金币
                        self._spawn_coins(zombie)
                        # 移除僵尸
                        zombie.kill()
                    
                    # 子弹被销毁
                    bullet.kill()
                    
                    # 每个子弹只能击中一个僵尸，所以处理完一个碰撞后就跳出循环
                    break
        
        # 检测玩家和金币的碰撞
        for coin in self.coins:
            if pygame.sprite.collide_rect(self.player, coin):
                # 收集金币
                coin_value = coin.collect((100, 50))  # 金币UI显示位置
                # 增加金币数量
                self.coin_system.add_coins(coin_value, coin.rect.center)
                # 触发金币显示动画
                self.coin_display.trigger_pulse()

    def _spawn_coins(self, zombie):
        """从僵尸生成金币
        
        Args:
            zombie: 被击杀的僵尸
        """
        # 获取僵尸的金币价值
        coin_value = getattr(zombie, "coin_value", 1)
        
        # 创建金币对象
        coin = Coin(zombie.rect.centerx, zombie.rect.centery, coin_value)
        self.coins.add(coin)
        self.all_sprites.add(coin)

    def update(self):
        """更新游戏状态"""
        if self.game_state != GAME_STATE_PLAYING:
            return
        
        # 检查鼠标左键是否按下，如果按下则尝试发射子弹
        if self.mouse_left_down and self.game_state == GAME_STATE_PLAYING:
            # 使用最后记录的鼠标位置发射子弹
            self.fire_bullet(self.last_mouse_pos[1])
        
        # 生成僵尸
        self.spawn_zombies()
        
        # 更新所有精灵
        # 对于玩家，只更新动画状态，不更新位置（位置更新由鼠标事件处理）
        for sprite in self.all_sprites:
            if sprite == self.player:
                # 不传入鼠标位置，只更新动画
                self.player.update()
            else:
                sprite.update()
        
        # 检测自动收集的金币
        for coin in self.coins:
            if coin.collected and not hasattr(coin, 'counted'):
                # 增加金币数量
                self.coin_system.add_coins(coin.value, coin.rect.center)
                # 触发金币显示动画
                self.coin_display.trigger_pulse()
                # 标记金币已计数，避免重复计算
                coin.counted = True
        
        # 更新粒子效果
        self.particles.update()
        
        # 更新金币系统
        self.coin_system.update_animations()
        self.coin_display.update()
        
        # 更新升级菜单
        self.upgrade_menu.update()
        
        # 检测碰撞
        self.check_collisions()
        
        # 检测僵尸是否到达左边缘
        for zombie in self.zombies:
            if zombie.update():
                self.game_state = GAME_STATE_GAME_OVER
                pygame.mixer.music.stop()

    def draw(self):
        """绘制游戏画面"""
        # 根据游戏状态绘制不同画面
        if self.game_state == GAME_STATE_START_MENU:
            # 绘制开始菜单背景
            self.screen.blit(self.background_start_menu, (0, 0))
            
            # 绘制按钮
            self.start_button.draw(self.screen)
            self.quit_button.draw(self.screen)
            
            # 绘制游戏标题
            self.text_renderer.render_text("炮打僵尸", (SCREEN_WIDTH // 2 - 150, 100), "game_over", (255, 0, 0))
            
        elif self.game_state == GAME_STATE_PLAYING:
            # 绘制游戏背景
            self.screen.blit(self.background_playing, (0, 0))
            
            # 绘制红色边界线，标识炮台不能超过的位置
            boundary_x = SCREEN_WIDTH // 2
            pygame.draw.line(self.screen, (255, 0, 0), (boundary_x, 0), (boundary_x, SCREEN_HEIGHT), 3)
            
            # 绘制所有精灵
            for sprite in self.all_sprites:
                if hasattr(sprite, 'render') and callable(getattr(sprite, 'render')):
                    sprite.render(self.screen)
                else:
                    self.screen.blit(sprite.image, sprite.rect)
                
            # 绘制粒子效果
            for particle in self.particles:
                self.screen.blit(particle.image, particle.rect)
            
            # 绘制金币UI
            self.coin_display.render(self.screen)
            
            # 绘制升级按钮
            self.upgrade_button.draw(self.screen)
            
            # 绘制暂停按钮
            self.pause_button.draw(self.screen)
            
            # 绘制波次信息
            wave_info = self.zombie_spawner.get_wave_info()
            if wave_info["state"] == "break":
                wave_text = f"第 {wave_info['wave']} 波结束，下一波还有 {wave_info['remaining']:.1f} 秒"
                self.text_renderer.render_text(wave_text, (SCREEN_WIDTH // 2 - 200, 50), "regular", (255, 255, 0))
            else:
                wave_text = f"第 {wave_info['wave']} 波进行中 ({wave_info['remaining']:.1f} 秒)"
                self.text_renderer.render_text(wave_text, (SCREEN_WIDTH // 2 - 150, 50), "regular", (255, 255, 255))
            
            # # 根据得分显示不同的提示
            # if 0 <= self.coin_system.coins <= 10:
            #     self.text_renderer.render_text("(阶段1)随着时间的推移 你会变强，但僵尸也会！", (270, 100), "regular", (0, 255, 255))
            # elif 210 <= self.coin_system.coins <= 250:
            #     self.text_renderer.render_text("(阶段2)觉得自己很帅？僵尸不这么想！！！，感受恐惧吧！！", (200, 100), "warning", (255, 0, 0))
            
        elif self.game_state == GAME_STATE_PAUSED:
            # 绘制暂停菜单
            self.screen.blit(self.background_playing, (0, 0))
            
            # 半透明背景
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 黑色半透明
            self.screen.blit(overlay, (0, 0))
            
            # 绘制暂停标题
            self.text_renderer.render_text("游戏暂停", (SCREEN_WIDTH // 2 - 150, 100), "regular", (255, 255, 255))
            
            # 绘制按钮
            self.resume_button.draw(self.screen)
            self.restart_button.draw(self.screen)
            self.menu_button.draw(self.screen)
            
        elif self.game_state == GAME_STATE_GAME_OVER:
            def game_over_screen(self):
                """显示游戏结束画面"""
                # 绘制游戏结束背景
                self.screen.blit(self.game_over_bg, (0, 0))
                
                # 绘制游戏结束文本
                self.text_renderer.render_text("游戏结束", SCREEN_WIDTH // 2, 150, font_size=80, font_type="game_over")
                self.text_renderer.render_text(f"得分: {self.score}", SCREEN_WIDTH // 2, 250, font_size=50)
                self.text_renderer.render_text(f"坚持时间: {self.get_survival_time_text()}", SCREEN_WIDTH // 2, 320, font_size=40)
                
                # 绘制重新开始和返回菜单按钮
                self.restart_button.draw(self.screen)
                self.menu_button.draw(self.screen)
                
                # 保存游戏数据
                self.save_manager.save_game()
                
            def complete_level(self, level_id, score):
                """完成关卡
                
                Args:
                    level_id: 关卡ID
                    score: 得分
                """
                # 更新存档数据
                self.save_manager.complete_level(level_id, score)
            self.text_renderer.render_text(f"最终金币: {self.coin_system.coins}", (SCREEN_WIDTH // 2 - 150, 200), "regular", (255, 255, 255))
            
            # 绘制按钮
            self.restart_button.draw(self.screen)
            self.menu_button.draw(self.screen)
        
        # 绘制升级菜单（如果激活）
        if self.upgrade_menu.active:
            self.upgrade_menu.render(self.screen)
    
    def run(self):
        """运行游戏主循环"""
        while True:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 绘制游戏画面
            self.draw()
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率
            self.clock.tick(FPS)
    
    def quit_game(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()