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

# 僵尸状态常量
ZOMBIE_MOVE = 0
ZOMBIE_STAND = 1
ZOMBIE_ATTACK = 2

# 资源路径常量
IMAGE_DIR = "img"
FONTS_DIR = os.path.join(IMAGE_DIR, "fonts")
ZOMBIE_MOVE_DIR = os.path.join(IMAGE_DIR, "move")
BACKGROUND_IMAGE = os.path.join(IMAGE_DIR, "background.jpg")
GAME_OVER_IMAGE = os.path.join(IMAGE_DIR, "game_over_screen.png")
CANNON_IMAGE = os.path.join(IMAGE_DIR, "cannon.png")
BULLET_IMAGE = os.path.join(IMAGE_DIR, "bullet.png")
BACKGROUND_MUSIC = os.path.join(IMAGE_DIR, "Laura Shigihara - Zombies On Your Lawn.mp3")

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
            frame_path = os.path.join(ZOMBIE_MOVE_DIR, f"{i:02d}.png")
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
        self.image = ResourceManager.load_image(CANNON_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT // 2 - self.rect.height // 2
        self.score = 0
    
    def update(self, mouse_y):
        """更新玩家位置
        
        Args:
            mouse_y: 鼠标的y坐标
        """
        # 根据鼠标位置更新大炮的y坐标
        self.rect.y = mouse_y - self.rect.height // 2
        
        # 确保大炮不会超出屏幕
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Game:
    """游戏主类，管理游戏状态和逻辑"""
    
    def __init__(self):
        """初始化游戏"""
        # 初始化pygame
        pygame.init()
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("炮打僵尸_无尽版")
        
        # 加载游戏资源
        self.background = ResourceManager.load_image(BACKGROUND_IMAGE)
        self.game_over_bg = ResourceManager.load_image(GAME_OVER_IMAGE)
        
        # 创建文本渲染器
        self.text_renderer = TextRenderer(self.screen)
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # 创建玩家
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # 游戏状态
        self.game_over = False
        self.start_time = time.time()
        self.zombie_spawn_timer = time.time()
        self.clock = pygame.time.Clock()
        self.paused = False
        
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
            
            # 暂停/继续游戏
            elif event.type == KEYDOWN and event.key == K_p:
                self.toggle_pause()
            
            # 重新开始游戏
            elif event.type == KEYDOWN and event.key == K_r and self.game_over:
                self.reset_game()
            
            # 鼠标移动事件
            elif event.type == MOUSEMOTION and not self.paused and not self.game_over:
                self.player.update(event.pos[1])
            
            # 鼠标点击事件 - 发射子弹
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and not self.paused and not self.game_over:
                self.fire_bullet(event.pos[1])
    
    def toggle_pause(self):
        """切换游戏暂停状态"""
        self.paused = not self.paused
        if self.paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    
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
        self.game_over = False
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
        bullet = Bullet(self.player.rect.right, y_pos - 20, bullet_speed)
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)
    
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
                zombie.kill()
                bullet.kill()
                self.player.score += 1
    
    def update(self):
        """更新游戏状态"""
        if self.paused or self.game_over:
            return
        
        # 生成僵尸
        self.spawn_zombies()
        
        # 更新所有精灵
        self.bullets.update()
        
        # 更新僵尸并检查是否有僵尸到达左边缘
        for zombie in self.zombies:
            if zombie.update():
                self.game_over = True
                pygame.mixer.music.stop()
        
        # 检测碰撞
        self.check_collisions()
    
    def draw(self):
        """绘制游戏画面"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        if self.game_over:
            # 绘制游戏结束画面
            self.screen.blit(self.game_over_bg, (0, 0))
            self.text_renderer.render_text("游戏结束！", (200, 200), "game_over", (255, 12, 3))
            self.text_renderer.render_text(f"最终得分: {self.player.score}", (200, 300), "regular", (255, 255, 255))
            self.text_renderer.render_text("按R键重新开始", (200, 400), "regular", (255, 255, 255))
        else:
            # 绘制所有精灵
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            
            # 绘制得分
            self.text_renderer.render_text(f"得分: {self.player.score}", (900, 10), "regular", (0, 0, 0))
            
            # 根据得分显示不同的提示
            if 0 <= self.player.score <= 10:
                self.text_renderer.render_text("(阶段1)随着时间的推移 你会变强，但僵尸也会！", (270, 100), "regular", (0, 255, 255))
            elif 210 <= self.player.score <= 250:
                self.text_renderer.render_text("(阶段2)觉得自己很帅？僵尸不这么想！！！，感受恐惧吧！！", (200, 100), "warning", (255, 0, 0))
            
            # 如果游戏暂停，显示暂停提示
            if self.paused:
                self.text_renderer.render_text("游戏暂停 - 按P继续", (400, 300), "regular", (255, 0, 0))
    
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
