#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
炮打僵尸游戏 (无尽版)

这是一个使用Pygame开发的简单射击游戏，玩家控制一门大炮射击不断涌来的僵尸。
游戏特点：
- 无尽模式：僵尸会不断生成，随着时间推移速度会加快
- 分数系统：实时显示玩家得分
- 游戏状态：根据得分不同显示不同的游戏提示

作者: 原始作者
重构: AI助手
"""

import pygame
import sys
import time
import random
import os
from pygame.locals import *

# 游戏常量定义
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# 游戏状态常量
GAME_STATE_START_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_PAUSED = 2
GAME_STATE_GAME_OVER = 3

# 僵尸状态常量
ZOMBIE_MOVE = 0
ZOMBIE_STAND = 1
ZOMBIE_ATTACK = 2

# 资源路径常量
IMAGE_DIR = "img"
FONTS_DIR = os.path.join(IMAGE_DIR, "fonts")
ZOMBIE_MOVE_DIR = os.path.join(IMAGE_DIR, "move")
BACKGROUND_PLAYING_IMAGE = os.path.join(IMAGE_DIR, "background_playing.jpg")
BACKGROUND_START_MENU_IMAGE = os.path.join(IMAGE_DIR, "background_start-menu.jpg")
GAME_OVER_IMAGE = os.path.join(IMAGE_DIR, "game_over_screen.png")
CANNON_IMAGE = os.path.join(IMAGE_DIR, "cannon_new.png")
BULLET_IMAGE = os.path.join(IMAGE_DIR, "bullet_new.png")
BUTTON_IMAGE = os.path.join(IMAGE_DIR, "button.png")
BACKGROUND_MUSIC = os.path.join(IMAGE_DIR, "Laura Shigihara - Zombies On Your Lawn.mp3")

# 音效路径常量
SOUND_DIR = "sound"
BULLET_FIRED_SOUND = os.path.join(SOUND_DIR, "bulletFired.mp3")

# 动画常量
ANIMATION_SPEED = 5  # 动画速度
SCORE_ANIMATION_DURATION = 30  # 得分动画持续帧数

# 字体文件常量
REGULAR_FONT = os.path.join(FONTS_DIR, "regular.ttf")
WARNING_FONT = os.path.join(FONTS_DIR, "warning.ttf")
GAME_OVER_FONT = os.path.join(FONTS_DIR, "game_over.ttf")


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
            return pygame.image.load(file_path)
        except pygame.error as e:
            print(f"无法加载图片: {file_path}")
            print(f"错误信息: {e}")
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
            return pygame.font.Font(file_path, size)
        except pygame.error as e:
            print(f"无法加载字体: {file_path}")
            print(f"错误信息: {e}")
            sys.exit(1)
    
    @staticmethod
    def load_sound(file_path):
        """加载音频资源
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            加载的音频对象
            
        Raises:
            pygame.error: 如果音频加载失败
        """
        try:
            return pygame.mixer.Sound(file_path)
        except pygame.error as e:
            print(f"无法加载音频: {file_path}")
            print(f"错误信息: {e}")
            return None


class TextRenderer:
    """文本渲染类，负责在屏幕上渲染各种文本"""
    
    def __init__(self, canvas):
        """初始化文本渲染器
        
        Args:
            canvas: 游戏画布对象
        """
        self.canvas = canvas
        self.fonts = {
            "regular": ResourceManager.load_font(REGULAR_FONT, 50),
            "warning": ResourceManager.load_font(WARNING_FONT, 80),
            "game_over": ResourceManager.load_font(GAME_OVER_FONT, 100)
        }
    
    def render_text(self, text, position, font_type="regular", color=(0, 0, 0)):
        """渲染文本到画布上
        
        Args:
            text: 要渲染的文本内容
            position: 文本位置，(x, y)元组
            font_type: 字体类型，可选值为"regular", "warning", "game_over"
            color: 文本颜色，RGB元组
        """
        if font_type not in self.fonts:
            font_type = "regular"
            
        text_surface = self.fonts[font_type].render(text, True, color)
        self.canvas.blit(text_surface, position)


class Bullet(pygame.sprite.Sprite):
    """子弹类，表示玩家发射的子弹"""
    
    def __init__(self, x, y, speed):
        """初始化子弹对象
        
        Args:
            x: 子弹的x坐标
            y: 子弹的y坐标
            speed: 子弹的移动速度
        """
        super().__init__()
        self.image = ResourceManager.load_image(BULLET_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = 20
        self.height = 20
        self.speed = speed
    
    def update(self):
        """更新子弹位置"""
        self.rect.x += self.speed
        
        # 如果子弹超出屏幕，将其移除
        if self.rect.left > SCREEN_WIDTH:
            self.kill()
    
    def check_hit(self, zombie):
        """检测子弹是否击中僵尸
        
        Args:
            zombie: 僵尸对象
            
        Returns:
            bool: 如果击中返回True，否则返回False
        """
        # 使用pygame的碰撞检测函数
        return pygame.sprite.collide_rect(self, zombie)


class Zombie(pygame.sprite.Sprite):
    """僵尸类，表示游戏中的敌人"""
    
    def __init__(self, y, speed):
        """初始化僵尸对象
        
        Args:
            y: 僵尸的y坐标
            speed: 僵尸的移动速度
        """
        super().__init__()
        self.speed = speed
        self.rect = pygame.Rect(SCREEN_WIDTH, y, 180, 180)
        self.state = ZOMBIE_MOVE
        self.index = 0
        
        # 加载僵尸移动动画帧
        self.move_frames = []
        for i in range(1, 14):
            frame_path = os.path.join(ZOMBIE_MOVE_DIR, f"zombie_move_{i:02d}.png")
            self.move_frames.append(ResourceManager.load_image(frame_path))
        
        # 当前显示的帧
        self.image = self.move_frames[0]
    
    def update(self):
        """更新僵尸状态和位置"""
        # 更新动画帧
        if self.state == ZOMBIE_MOVE:
            self.image = self.move_frames[self.index % len(self.move_frames)]
            self.rect.x -= self.speed
        
        self.index += 1
        
        # 如果僵尸到达屏幕左边缘，返回True表示游戏结束
        if self.rect.right <= 0:
            return True
        return False


class Player(pygame.sprite.Sprite):
    """玩家类，表示玩家控制的大炮"""
    
    def __init__(self):
        """初始化玩家对象"""
        super().__init__()
        self.original_image = ResourceManager.load_image(CANNON_IMAGE)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.initial_x = 20  # 设置初始x坐标，留出后坐力空间
        self.rect.x = self.initial_x
        self.rect.y = SCREEN_HEIGHT // 2 - self.rect.height // 2
        self.score = 0
        
        # 发射动画相关
        self.is_firing = False
        self.firing_frame = 0
        self.firing_max_frames = 15  # 增加帧数使动画更流畅
        self.recoil_offset = 0  # 后坐力位移
        self.original_center = None  # 存储原始中心点
        
        # 得分动画相关
        self.score_animations = []
    
    def update(self, mouse_y=None):
        """更新玩家位置和动画状态
        
        Args:
            mouse_y: 鼠标的y坐标，如果为None则只更新动画状态
        """
        # 如果提供了鼠标位置，则更新炮台的垂直位置
        if mouse_y is not None:
            # 如果正在发射动画中，记录新的目标y坐标
            if self.is_firing and self.original_center is not None:
                # 更新原始中心点的y坐标，保持x坐标不变
                self.original_center = (self.original_center[0], mouse_y - self.rect.height // 2 + self.rect.height // 2)
            else:
                # 根据鼠标位置更新大炮的y坐标
                self.rect.y = mouse_y - self.rect.height // 2
            
            # 确保大炮不会超出屏幕
            target_y = mouse_y - self.rect.height // 2
            if target_y < 0:
                target_y = 0
            elif target_y + self.rect.height > SCREEN_HEIGHT:
                target_y = SCREEN_HEIGHT - self.rect.height
                
            # 如果不在发射动画中，直接更新位置
            if not self.is_firing:
                self.rect.y = target_y
        
        # 更新发射动画
        if self.is_firing:
            self.firing_frame += 1
            # 使用缓动函数使动画更加平滑
            progress = self.firing_frame / self.firing_max_frames
            
            # 前半段使用快速缓出函数，后半段使用缓入函数
            if progress < 0.5:
                # 前半段：快速后退（后坐力）
                half_progress = progress * 2  # 0-0.5 映射到 0-1
                eased_progress = 1 - (1 - half_progress) * (1 - half_progress)  # 二次缓出
                self.recoil_offset = -12 * eased_progress  # 减小后坐力位移
            else:
                # 后半段：缓慢恢复
                half_progress = (progress - 0.5) * 2  # 0.5-1 映射到 0-1
                eased_progress = half_progress * half_progress  # 二次缓入
                self.recoil_offset = -12 * (1 - eased_progress)  # 减小后坐力恢复
            
            # 发射动画效果：缩放和旋转
            if progress < 0.3:  # 前30%的时间快速缩小
                scale_factor = 1.0 - 0.08 * (progress / 0.3)  # 减小缩放幅度
            else:  # 后70%的时间缓慢恢复
                recovery_progress = (progress - 0.3) / 0.7
                scale_factor = 0.92 + 0.08 * recovery_progress  # 减小缩放幅度
                
            rotation_angle = -5 * self.recoil_offset / -12  # 减小旋转角度
            
            # 缩放原始图像
            scaled_image = pygame.transform.scale(self.original_image, 
                                               (int(self.original_image.get_width() * scale_factor),
                                                int(self.original_image.get_height() * scale_factor)))
            
            # 旋转缩放后的图像
            self.image = pygame.transform.rotate(scaled_image, rotation_angle)
            
            # 保持炮台位置跟随鼠标移动，同时应用后坐力位移
            if self.original_center is None:
                self.original_center = self.rect.center
                
            self.rect = self.image.get_rect()
            self.rect.centery = self.original_center[1]  # 使用当前的垂直位置
            self.rect.x = self.initial_x + self.recoil_offset  # 基于初始位置应用后坐力位移
            
            # 动画结束，恢复原始图像
            if self.firing_frame >= self.firing_max_frames:
                self.is_firing = False
                self.firing_frame = 0
                self.recoil_offset = 0
                self.image = self.original_image.copy()
                self.rect = self.image.get_rect()
                self.rect.centery = self.original_center[1]
                self.rect.x = self.initial_x
                self.original_center = None  # 重置原始中心点
    
    def fire(self):
        """触发发射动画"""
        self.is_firing = True
        self.firing_frame = 0
        self.original_center = self.rect.center  # 记录发射前的中心位置
        # 立即应用初始后坐力效果，使动画更加连贯
        self.recoil_offset = 0
    
    def add_score_animation(self, score, position):
        """添加得分动画
        
        Args:
            score: 增加的得分
            position: 动画起始位置
        """
        self.score_animations.append({
            "score": score,
            "position": position,
            "frame": 0
        })


class Button(pygame.sprite.Sprite):
    """按钮类，用于游戏菜单"""
    
    def __init__(self, x, y, width, height, text, font_size=40, font_type="regular"):
        """初始化按钮对象
        
        Args:
            x: 按钮的x坐标
            y: 按钮的y坐标
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            font_size: 字体大小
            font_type: 字体类型
        """
        super().__init__()
        self.original_image = ResourceManager.load_image(BUTTON_IMAGE)
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text = text
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.Font(REGULAR_FONT, font_size)
        
    def draw(self, surface):
        """绘制按钮
        
        Args:
            surface: 绘制的目标表面
        """
        # 绘制按钮背景
        surface.blit(self.image, self.rect)
        
        # 绘制按钮文本
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        """检测按钮是否被点击
        
        Args:
            pos: 鼠标点击位置
            
        Returns:
            bool: 如果点击返回True，否则返回False
        """
        return self.rect.collidepoint(pos)


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
            "bullet_fired": ResourceManager.load_sound(BULLET_FIRED_SOUND)
        }
        
        # 创建文本渲染器
        self.text_renderer = TextRenderer(self.screen)
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # 创建按钮
        self.start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 80, "开始游戏")
        self.quit_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 80, "退出游戏")
        self.resume_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 80, "继续游戏")
        self.restart_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 80, "重新开始")
        self.menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 300, 80, "返回菜单")
        
        # 创建玩家
        self.player = None
        
        # 游戏状态
        self.game_state = GAME_STATE_START_MENU
        self.start_time = 0
        self.zombie_spawn_timer = 0
        self.clock = pygame.time.Clock()
        
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
            
            # 鼠标点击事件
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # 开始菜单状态
                if self.game_state == GAME_STATE_START_MENU:
                    if self.start_button.is_clicked(mouse_pos):
                        self.start_game()
                    elif self.quit_button.is_clicked(mouse_pos):
                        self.quit_game()
                
                # 游戏进行状态
                elif self.game_state == GAME_STATE_PLAYING:
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
            
            # 鼠标移动事件 - 允许炮台在发射动画状态时也能移动
            elif event.type == MOUSEMOTION and self.game_state == GAME_STATE_PLAYING:
                self.player.update(event.pos[1])
            
            # 暂停/继续游戏
            elif event.type == KEYDOWN and event.key == K_p and self.game_state == GAME_STATE_PLAYING:
                self.pause_game()
    
    def start_game(self):
        """开始新游戏"""
        # 清空所有精灵组
        self.all_sprites.empty()
        self.zombies.empty()
        self.bullets.empty()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
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
        
        # 重新创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 重置游戏状态
        self.game_state = GAME_STATE_PLAYING
        self.start_time = time.time()
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
        # 计算子弹速度 (随时间增加)
        game_time = time.time() - self.start_time
        bullet_speed = min(10, 5 + game_time // 60)  # 最大速度为10
        
        # 创建子弹对象
        bullet = Bullet(self.player.rect.right, y_pos - 40, bullet_speed)
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)
        
        # 触发炮台发射动画
        self.player.fire()
        
        # 播放发射音效
        if self.sounds["bullet_fired"]:
            self.sounds["bullet_fired"].play()
    
    def spawn_zombies(self):
        """生成僵尸"""
        current_time = time.time()
        game_time = current_time - self.start_time
        
        # 根据游戏时间调整僵尸生成频率
        spawn_interval = max(1.0, 2.0 - game_time / 120)  # 最小间隔为1秒
        
        if current_time - self.zombie_spawn_timer >= spawn_interval:
            self.zombie_spawn_timer = current_time
            
            # 根据游戏时间调整僵尸数量和速度
            zombie_count = min(5, 1 + int(game_time // 60))  # 最多同时生成5个
            
            for _ in range(zombie_count):
                y = random.randint(0, SCREEN_HEIGHT - 180)  # 僵尸高度为180
                speed = random.randint(1, min(5, 1 + int(game_time // 30)))  # 最大速度为5
                
                zombie = Zombie(y, speed)
                self.zombies.add(zombie)
                self.all_sprites.add(zombie)
    
    def check_collisions(self):
        """检测碰撞"""
        # 检测子弹和僵尸的碰撞
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.zombies, False)
            for zombie in hits:
                # 获取僵尸位置，用于显示得分动画
                zombie_pos = (zombie.rect.centerx, zombie.rect.centery)
                
                # 击杀僵尸
                zombie.kill()
                bullet.kill()
                
                # 增加得分
                self.player.score += 1
                
                # 添加得分动画
                self.player.add_score_animation(1, zombie_pos)
    
    def update(self):
        """更新游戏状态"""
        if self.game_state != GAME_STATE_PLAYING:
            return
        
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
            # 绘制开始菜单
            self.screen.blit(self.background_start_menu, (0, 0))
            
            # 绘制游戏标题
            self.text_renderer.render_text("炮打僵尸", (SCREEN_WIDTH // 2 - 150, 100), "game_over", (255, 255, 255))
            
            # 绘制按钮
            self.start_button.draw(self.screen)
            self.quit_button.draw(self.screen)
            
        elif self.game_state == GAME_STATE_PLAYING:
            # 绘制游戏背景
            self.screen.blit(self.background_playing, (0, 0))
            
            # 绘制所有精灵
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            
            # 绘制得分
            score_text = f"得分: {self.player.score}"
            self.text_renderer.render_text(score_text, (SCREEN_WIDTH - 250, 20), "regular", (255, 255, 255))
            
            # 绘制得分动画
            for anim in self.player.score_animations[:]:  # 使用副本进行迭代
                # 计算动画位置和透明度
                pos_y = anim["position"][1] - anim["frame"] // 2  # 向上移动
                alpha = 255 - int(255 * (anim["frame"] / SCORE_ANIMATION_DURATION))  # 逐渐变透明
                
                # 创建带透明度的文本
                font = pygame.font.Font(REGULAR_FONT, 30)
                text = font.render(f"+{anim['score']}", True, (255, 255, 0))
                text.set_alpha(alpha)
                
                # 绘制文本
                self.screen.blit(text, (anim["position"][0], pos_y))
                
                # 更新动画帧
                anim["frame"] += 1
                
                # 移除完成的动画
                if anim["frame"] >= SCORE_ANIMATION_DURATION:
                    self.player.score_animations.remove(anim)
            
            # 根据得分显示不同的提示
            if 0 <= self.player.score <= 10:
                self.text_renderer.render_text("(阶段1)随着时间的推移 你会变强，但僵尸也会！", (270, 100), "regular", (0, 255, 255))
            elif 210 <= self.player.score <= 250:
                self.text_renderer.render_text("(阶段2)觉得自己很帅？僵尸不这么想！！！，感受恐惧吧！！", (200, 100), "warning", (255, 0, 0))
            
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
            # 绘制游戏结束画面
            self.screen.blit(self.game_over_bg, (0, 0))
            
            # 绘制游戏结束文本
            self.text_renderer.render_text("游戏结束！", (SCREEN_WIDTH // 2 - 200, 100), "game_over", (255, 12, 3))
            self.text_renderer.render_text(f"最终得分: {self.player.score}", (SCREEN_WIDTH // 2 - 150, 200), "regular", (255, 255, 255))
            
            # 绘制按钮
            self.restart_button.draw(self.screen)
            self.menu_button.draw(self.screen)
    
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


if __name__ == "__main__":
    # 创建并运行游戏
    game = Game()
    game.run()
