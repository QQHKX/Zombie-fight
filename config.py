import os

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

# 游戏难度常量
INITIAL_WAVE_ZOMBIES = 5  # 第一波僵尸数量

# 资源路径常量
ASSETS_DIR = "assets"
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")
ZOMBIE_MOVE_DIR = os.path.join(IMAGE_DIR, "move")
BACKGROUND_PLAYING_IMAGE = os.path.join(IMAGE_DIR, "background_playing.jpg")
BACKGROUND_START_MENU_IMAGE = os.path.join(IMAGE_DIR, "background_start-menu.jpg")
GAME_OVER_IMAGE = os.path.join(IMAGE_DIR, "game_over_screen.png")
CANNON_IMAGE = os.path.join(IMAGE_DIR, "cannon_new.png")
CANNON_FIRE_IMAGE = os.path.join(IMAGE_DIR, "cannon_fire.png")  # 添加炮台发射图像
BULLET_IMAGE = os.path.join(IMAGE_DIR, "bullet_new.png")
BUTTON_IMAGE = os.path.join(IMAGE_DIR, "button.png")
BACKGROUND_MUSIC = os.path.join(IMAGE_DIR, "Laura Shigihara - Zombies On Your Lawn.mp3")

# 音效路径常量
BULLET_FIRED_SOUND = os.path.join(SOUND_DIR, "bulletFired.mp3")
HIT_SOUND = os.path.join(SOUND_DIR, "hit.mp3")

# 动画常量
ANIMATION_SPEED = 5  # 动画速度
SCORE_ANIMATION_DURATION = 30  # 得分动画持续帧数

# 字体文件常量
REGULAR_FONT = os.path.join(FONTS_DIR, "regular.ttf")
WARNING_FONT = os.path.join(FONTS_DIR, "warning.ttf")
GAME_OVER_FONT = os.path.join(FONTS_DIR, "game_over.ttf")
