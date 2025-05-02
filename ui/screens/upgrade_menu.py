import pygame
import time
from config import *
from core.resource_manager import ResourceManager

class UpgradeMenu:
    """升级菜单类，显示可用的升级选项"""
    
    def __init__(self, game):
        """初始化升级菜单
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.active = False
        
        # 加载背景和UI元素
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.background.fill((0, 0, 0, 180))  # 半透明黑色背景
        
        # 标题
        self.title_font = pygame.font.Font(GAME_OVER_FONT, 48)
        self.title_text = self.title_font.render("升级武器", True, (255, 215, 0))
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        
        # 金币显示
        self.coin_font = pygame.font.Font(REGULAR_FONT, 32)
        
        # 关闭按钮 - 移到左上角
        self.close_button = CloseButton(50, 50, 40, 40)
        
        # 升级按钮
        self.upgrade_buttons = []
        self._create_upgrade_buttons()
        
        # 确认对话框
        self.confirm_dialog = None
        
        # 提示消息
        self.message = None
        self.message_start_time = 0
        self.message_duration = 2.0  # 消息显示时间（秒）
        
        # 记录打开菜单前的游戏状态
        self.previous_game_state = None
    
    def show(self):
        """显示升级菜单"""
        self.active = True
        self._update_buttons()
        
        # 保存当前游戏状态并暂停游戏
        if self.game.game_state == GAME_STATE_PLAYING:
            self.previous_game_state = self.game.game_state
            self.game.pause_game()
    
    def hide(self):
        """隐藏升级菜单"""
        self.active = False
        self.confirm_dialog = None
        
        # 恢复游戏状态
        if self.previous_game_state == GAME_STATE_PLAYING:
            self.game.resume_game()
            self.previous_game_state = None
    
    def handle_event(self, event):
        """处理事件
        
        Args:
            event: pygame事件
        
        Returns:
            bool: 是否处理了事件
        """
        if not self.active:
            return False
        
        # 如果有确认对话框，优先处理
        if self.confirm_dialog:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.confirm_dialog.handle_click(event.pos)
                if result is not None:
                    if result:  # 确认购买
                        self._purchase_upgrade(self.confirm_dialog.upgrade_type)
                    self.confirm_dialog = None
                    return True
            return True  # 即使没有点击确认对话框，也算处理了事件
        
        # 处理关闭按钮
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button.is_clicked(event.pos):
                self.hide()
                return True
            
            # 处理升级按钮
            for button in self.upgrade_buttons:
                if button.is_clicked(event.pos):
                    self._show_confirm_dialog(button.upgrade_type)
                    return True
        
        return True  # 即使没有点击任何按钮，也算处理了事件
    
    def update(self):
        """更新升级菜单状态"""
        if not self.active:
            return
        
        # 更新按钮状态
        self._update_buttons()
        
        # 更新消息状态
        if self.message and time.time() - self.message_start_time > self.message_duration:
            self.message = None
    
    def render(self, screen):
        """渲染升级菜单
        
        Args:
            screen: 游戏屏幕
        """
        if not self.active:
            return
        
        # 绘制半透明背景
        screen.blit(self.background, (0, 0))
        
        # 绘制标题
        screen.blit(self.title_text, self.title_rect)
        
        # 绘制金币显示
        coin_text = self.coin_font.render(f"金币: {self.game.coin_system.coins}", True, (255, 215, 0))
        screen.blit(coin_text, (50, 50))
        
        # 绘制关闭按钮
        self.close_button.render(screen)
        
        # 绘制升级按钮
        for button in self.upgrade_buttons:
            button.render(screen)
        
        # 绘制确认对话框
        if self.confirm_dialog:
            self.confirm_dialog.render(screen)
        
        # 绘制消息
        if self.message:
            message_font = pygame.font.Font(REGULAR_FONT, 24)
            message_text = message_font.render(self.message, True, (255, 255, 255))
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            screen.blit(message_text, message_rect)
    
    def _create_upgrade_buttons(self):
        """创建升级按钮"""
        # 获取可用的升级类型
        upgrade_types = list(self.game.upgrade_system.upgrades.keys())
        
        # 计算按钮位置
        button_width = 200
        button_height = 250
        button_margin = 50
        total_width = len(upgrade_types) * button_width + (len(upgrade_types) - 1) * button_margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # 创建按钮
        for i, upgrade_type in enumerate(upgrade_types):
            x = start_x + i * (button_width + button_margin)
            y = SCREEN_HEIGHT // 2 - button_height // 2
            
            button = UpgradeButton(
                x, y, button_width, button_height,
                self.game.upgrade_system.upgrades[upgrade_type],
                upgrade_type,
                self.game.upgrade_system,
                self.game.weapon_upgrades
            )
            self.upgrade_buttons.append(button)
    
    def _update_buttons(self):
        """更新按钮状态"""
        for button in self.upgrade_buttons:
            button.update_status()
    
    def _show_confirm_dialog(self, upgrade_type):
        """显示购买确认对话框
        
        Args:
            upgrade_type: 升级类型
        """
        # 获取升级价格
        price = self.game.upgrade_system.get_upgrade_price(upgrade_type)
        
        # 如果价格为0（已达到最高级或无法购买），不显示确认对话框
        if price <= 0:
            return
        
        # 创建确认对话框
        self.confirm_dialog = ConfirmDialog(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 200,
            f"确认花费 {price} 金币购买 {self.game.upgrade_system.upgrades[upgrade_type]['name']} 吗？",
            upgrade_type
        )
    
    def _purchase_upgrade(self, upgrade_type):
        """购买升级
        
        Args:
            upgrade_type: 升级类型
        """
        # 尝试购买升级
        if self.game.upgrade_system.purchase_upgrade(upgrade_type):
            self.message = f"升级成功！"
        else:
            self.message = f"升级失败，金币不足！"
        
        self.message_start_time = time.time()
        
        # 更新按钮状态
        self._update_buttons()

class UpgradeButton:
    """升级按钮类"""
    
    def __init__(self, x, y, width, height, upgrade, upgrade_type, upgrade_system, weapon_upgrades):
        """初始化升级按钮
        
        Args:
            x: 按钮x坐标
            y: 按钮y坐标
            width: 按钮宽度
            height: 按钮高度
            upgrade: 升级数据
            upgrade_type: 升级类型
            upgrade_system: 升级系统实例
            weapon_upgrades: 武器升级实例
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade = upgrade
        self.upgrade_type = upgrade_type
        self.upgrade_system = upgrade_system
        self.weapon_upgrades = weapon_upgrades
        
        # 按钮状态
        self.can_purchase = False
        self.max_level = False
        
        # 鼠标悬停状态
        self.is_hovered = False
        self.border_width = 2  # 正常边框宽度
        self.hover_border_width = 4  # 悬停时边框宽度
        
        # 字体
        self.title_font = pygame.font.Font(REGULAR_FONT, 24)
        self.desc_font = pygame.font.Font(REGULAR_FONT, 18)
        self.price_font = pygame.font.Font(REGULAR_FONT, 20)
        
        # 更新状态
        self.update_status()
    
    def update_status(self):
        """更新按钮状态"""
        # 获取当前等级和最大等级
        current_level = self.upgrade["level"]
        max_level = self.upgrade["max_level"]
        
        # 检查是否已达到最大等级
        self.max_level = current_level >= max_level
        
        # 获取升级价格
        price = self.upgrade_system.get_upgrade_price(self.upgrade_type)
        
        # 检查是否可以购买
        self.can_purchase = not self.max_level and price > 0 and self.upgrade_system.game.coin_system.coins >= price
    
    def is_clicked(self, pos):
        """检查是否点击了按钮
        
        Args:
            pos: 鼠标位置
        
        Returns:
            bool: 是否点击了按钮
        """
        return self.rect.collidepoint(pos)
    
    def render(self, screen):
        """渲染按钮
        
        Args:
            screen: 游戏屏幕
        """
        # 检查鼠标悬停状态
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 确定边框宽度
        border_width = self.hover_border_width if self.is_hovered else self.border_width
        
        # 绘制按钮背景
        if self.max_level:
            # 已达到最大等级，使用金色背景
            color = (200, 170, 0)
        elif self.can_purchase:
            # 可以购买，使用绿色背景
            color = (0, 150, 0)
        else:
            # 无法购买，使用灰色背景
            color = (100, 100, 100)
        
        # 如果鼠标悬停，使颜色更亮
        if self.is_hovered:
            r, g, b = color
            color = (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255))
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_width)  # 白色边框
        
        # 绘制标题
        title_text = self.title_font.render(self.upgrade["name"], True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(title_text, title_rect)
        
        # 绘制等级
        level_text = self.desc_font.render(
            f"等级: {self.upgrade['level']}/{self.upgrade['max_level']}", 
            True, (255, 255, 255)
        )
        level_rect = level_text.get_rect(centerx=self.rect.centerx, top=title_rect.bottom + 10)
        screen.blit(level_text, level_rect)
        
        # 绘制效果描述
        desc_text = self.weapon_upgrades.get_upgrade_description(
            self.upgrade_type, self.upgrade["level"]
        )
        desc_lines = desc_text.split('\n')
        for i, line in enumerate(desc_lines):
            line_text = self.desc_font.render(line, True, (255, 255, 255))
            line_rect = line_text.get_rect(centerx=self.rect.centerx, top=level_rect.bottom + 10 + i * 20)
            screen.blit(line_text, line_rect)
        
        # 绘制预览
        preview_y = level_rect.bottom + 10 + len(desc_lines) * 20 + 30
        self.weapon_upgrades.render_upgrade_preview(
            screen, self.upgrade_type, self.upgrade["level"],
            (self.rect.centerx, preview_y)
        )
        
        # 绘制价格
        if self.max_level:
            price_text = self.price_font.render("已达最大等级", True, (255, 255, 255))
        else:
            price = self.upgrade_system.get_upgrade_price(self.upgrade_type)
            price_text = self.price_font.render(f"价格: {price} 金币", True, (255, 255, 255))
        
        price_rect = price_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 10)
        screen.blit(price_text, price_rect)

class CloseButton:
    """关闭按钮类"""
    
    def __init__(self, x, y, width, height):
        """初始化关闭按钮
        
        Args:
            x: 按钮x坐标
            y: 按钮y坐标
            width: 按钮宽度
            height: 按钮高度
        """
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        
        # 鼠标悬停状态
        self.is_hovered = False
        self.normal_color = (200, 0, 0)  # 正常状态下的颜色
        self.hover_color = (255, 50, 50)  # 悬停状态下的颜色
        self.current_color = self.normal_color  # 当前颜色
    
    def is_clicked(self, pos):
        """检查是否点击了按钮
        
        Args:
            pos: 鼠标位置
        
        Returns:
            bool: 是否点击了按钮
        """
        return self.rect.collidepoint(pos)
    
    def render(self, screen):
        """渲染按钮
        
        Args:
            screen: 游戏屏幕
        """
        # 检查鼠标悬停状态
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 根据悬停状态设置颜色
        self.current_color = self.hover_color if self.is_hovered else self.normal_color
        
        # 绘制按钮背景
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # 白色边框
        
        # 绘制X
        margin = 10
        pygame.draw.line(screen, (255, 255, 255), 
                        (self.rect.left + margin, self.rect.top + margin),
                        (self.rect.right - margin, self.rect.bottom - margin), 3)
        pygame.draw.line(screen, (255, 255, 255), 
                        (self.rect.left + margin, self.rect.bottom - margin),
                        (self.rect.right - margin, self.rect.top + margin), 3)

class ConfirmDialog:
    """确认对话框类"""
    
    def __init__(self, x, y, width, height, message, upgrade_type):
        """初始化确认对话框
        
        Args:
            x: 对话框x坐标
            y: 对话框y坐标
            width: 对话框宽度
            height: 对话框高度
            message: 对话框消息
            upgrade_type: 升级类型
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.message = message
        self.upgrade_type = upgrade_type
        
        # 创建按钮
        button_width = 100
        button_height = 40
        button_margin = 20
        
        self.confirm_button = pygame.Rect(
            x + width // 2 - button_width - button_margin // 2,
            y + height - button_height - 20,
            button_width, button_height
        )
        
        self.cancel_button = pygame.Rect(
            x + width // 2 + button_margin // 2,
            y + height - button_height - 20,
            button_width, button_height
        )
        
        # 字体
        self.font = pygame.font.Font(REGULAR_FONT, 20)
        self.button_font = pygame.font.Font(REGULAR_FONT, 18)
    
    def handle_click(self, pos):
        """处理点击事件
        
        Args:
            pos: 鼠标位置
        
        Returns:
            bool or None: True表示确认，False表示取消，None表示未点击按钮
        """
        if self.confirm_button.collidepoint(pos):
            return True
        elif self.cancel_button.collidepoint(pos):
            return False
        return None
    
    def render(self, screen):
        """渲染对话框
        
        Args:
            screen: 游戏屏幕
        """
        # 绘制对话框背景
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # 白色边框
        
        # 绘制消息
        # 将消息拆分成多行
        words = self.message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            # 检查行宽度
            if self.font.size(test_line)[0] < self.rect.width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
        
        # 绘制每一行
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.top + 20 + i * 30)
            screen.blit(text, text_rect)
        
        # 绘制按钮
        # 确认按钮
        pygame.draw.rect(screen, (0, 150, 0), self.confirm_button)
        pygame.draw.rect(screen, (255, 255, 255), self.confirm_button, 2)  # 白色边框
        confirm_text = self.button_font.render("确认", True, (255, 255, 255))
        confirm_rect = confirm_text.get_rect(center=self.confirm_button.center)
        screen.blit(confirm_text, confirm_rect)
        
        # 取消按钮
        pygame.draw.rect(screen, (150, 0, 0), self.cancel_button)
        pygame.draw.rect(screen, (255, 255, 255), self.cancel_button, 2)  # 白色边框
        cancel_text = self.button_font.render("取消", True, (255, 255, 255))
        cancel_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_rect)