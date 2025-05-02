import pygame
import sys
import time
from config import *
from core.game import Game

def main():
    # 初始化游戏
    game = Game()
    
    # 设置测试模式
    game.game_state = GAME_STATE_PLAYING
    
    # 主循环
    clock = pygame.time.Clock()
    running = True
    
    # 测试变量
    zombie_types = ["normal", "fast", "tank"]
    current_type_index = 0
    current_level = 1
    
    # 保存原始的update方法
    original_update = game.update
    
    # 重写update方法，禁用游戏结束检测和僵尸自然生成
    def test_update():
        """测试模式下的更新方法，禁用游戏结束检测和僵尸自然生成"""
        if game.game_state != GAME_STATE_PLAYING:
            return
        
        # 检查鼠标左键是否按下，如果按下则尝试发射子弹
        if game.mouse_left_down and game.game_state == GAME_STATE_PLAYING:
            # 使用最后记录的鼠标位置发射子弹
            game.fire_bullet(game.last_mouse_pos[1])
        
        # 测试模式下禁用僵尸自然生成
        # game.spawn_zombies()  # 注释掉这行，禁用自然生成
        
        # 更新所有精灵
        for sprite in game.all_sprites:
            if sprite == game.player:
                # 不传入鼠标位置，只更新动画
                game.player.update()
            else:
                sprite.update()
        
        # 检测自动收集的金币
        for coin in game.coins:
            if coin.collected and not hasattr(coin, 'counted'):
                # 增加金币数量
                game.coin_system.add_coins(coin.value, coin.rect.center)
                # 触发金币显示动画
                game.coin_display.trigger_pulse()
                # 标记金币已计数，避免重复计算
                coin.counted = True
        
        # 更新粒子效果
        game.particles.update()
        
        # 更新金币系统
        game.coin_system.update_animations()
        game.coin_display.update()
        
        # 更新升级菜单
        game.upgrade_menu.update()
        
        # 自定义碰撞检测，避免使用game.check_collisions()
        # 只检测子弹和僵尸的碰撞
        for bullet in game.bullets:
            for zombie in game.zombies:
                if bullet.check_hit(zombie):
                    # 僵尸受到伤害
                    if zombie.take_damage(bullet.damage):
                        # 僵尸死亡，生成金币
                        game._spawn_coins(zombie)
                        # 移除僵尸
                        zombie.kill()
                    else:
                        # 创建打击粒子效果
                        game.create_hit_particles(zombie.rect.center)
                    
                    # 播放打击音效
                    if game.sounds["hit"]:
                        game.sounds["hit"].play()
                    
                    # 子弹被销毁
                    bullet.kill()
                    
                    # 每个子弹只能击中一个僵尸，所以处理完一个碰撞后就跳出循环
                    break
        
        # 测试模式下不检测僵尸是否到达左边缘，游戏不会结束
    
    # 替换update方法
    game.update = test_update
    
    print("=== 僵尸测试模式 ===")
    print("左键点击: 在鼠标位置放置僵尸")
    print("1-5键: 设置僵尸等级")
    print("Tab键: 切换僵尸类型")
    print("空格键: 发射全屏子弹（对所有僵尸造成伤害）")
    print("ESC键: 退出测试")
    print("注意: 测试模式下僵尸超出屏幕不会导致游戏结束")
    print("注意: 测试模式下已禁用僵尸自然生成，只能通过点击鼠标手动生成僵尸")
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 键盘事件
            elif event.type == pygame.KEYDOWN:
                # ESC键退出
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Tab键切换僵尸类型
                elif event.key == pygame.K_TAB:
                    current_type_index = (current_type_index + 1) % len(zombie_types)
                    print(f"当前僵尸类型: {zombie_types[current_type_index]}")
                
                # 数字键1-5设置僵尸等级
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    current_level = event.key - pygame.K_0  # 将键值转换为1-5
                    print(f"当前僵尸等级: {current_level}")
                
                # 空格键发射全屏子弹
                elif event.key == pygame.K_SPACE:
                    # 创建一个高伤害的子弹
                    from entities.bullet import Bullet
                    
                    # 创建全屏闪光效果
                    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, 100))  # 半透明白色
                    game.screen.blit(flash_surface, (0, 0))
                    pygame.display.flip()  # 立即更新屏幕
                    pygame.time.delay(50)  # 短暂延迟，让闪光效果可见
                    
                    # 创建简单的圆形扩散效果
                    for radius in range(0, SCREEN_WIDTH // 2, 40):  # 每40像素绘制一个圆
                        # 清除上一帧
                        game.screen.blit(game.background_playing, (0, 0))
                        # 绘制所有精灵
                        for sprite in game.all_sprites:
                            if hasattr(sprite, 'render') and callable(getattr(sprite, 'render')):
                                sprite.render(game.screen)
                            else:
                                game.screen.blit(sprite.image, sprite.rect)
                        # 绘制扩散圆 - 使用不透明颜色
                        pygame.draw.circle(game.screen, (200, 200, 255), 
                                         (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
                                         radius, 3)
                        pygame.display.flip()
                        pygame.time.delay(10)  # 短暂延迟，控制动画速度
                    
                    # 对每个僵尸造成伤害
                    zombies_hit = 0
                    for zombie in list(game.zombies):
                        # 对僵尸造成伤害
                        if zombie.take_damage(1):  # 造成50点伤害
                            # 僵尸死亡，生成金币
                            game._spawn_coins(zombie)
                            # 移除僵尸
                            zombie.kill()
                            zombies_hit += 1
                        else:
                            # 创建打击粒子效果
                            game.create_hit_particles(zombie.rect.center)
                            zombies_hit += 1
                    
                    # 播放打击音效
                    if zombies_hit > 0 and game.sounds["hit"]:
                        game.sounds["hit"].play()
                    
                    print(f"全屏子弹击中了{zombies_hit}个僵尸")
            
            # 鼠标点击事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 获取鼠标位置
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # 生成僵尸
                    zombie_type = zombie_types[current_type_index]
                    zombie = game.zombie_spawner.spawn_specific_zombie(
                        zombie_type, current_level, mouse_x, mouse_y
                    )
                    
                    if zombie:
                        print(f"在位置({mouse_x}, {mouse_y})生成了{current_level}级{zombie_type}僵尸")
        
        # 更新游戏状态
        game.update()
        
        # 渲染游戏
        # 绘制背景
        game.screen.blit(game.background_playing, (0, 0))
        
        # 绘制所有精灵（使用render方法而不是draw方法）
        for sprite in game.all_sprites:
            if hasattr(sprite, 'render') and callable(getattr(sprite, 'render')):
                sprite.render(game.screen)
            else:
                game.screen.blit(sprite.image, sprite.rect)
        
        # 显示当前测试信息
        font = pygame.font.Font(None, 24)
        info_text = f"类型: {zombie_types[current_type_index]} | 等级: {current_level} | 左键点击放置 | 测试模式"
        text_surface = font.render(info_text, True, (255, 255, 255))
        game.screen.blit(text_surface, (10, 10))
        
        # 更新显示
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(60)
    
    # 恢复原始的update方法
    game.update = original_update
    
    # 退出游戏
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()