#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
戴夫的炮击实验 - 主入口文件

这是一个使用Pygame开发的简单射击游戏，玩家控制一门大炮射击不断涌来的僵尸。
游戏特点：
- 无尽模式：僵尸会不断生成，随着时间推移速度会加快
- 分数系统：实时显示玩家得分
- 游戏状态：根据得分不同显示不同的游戏提示

作者: 原始作者
重构: AI助手
"""

from core.game import Game


def main():
    """游戏主函数"""
    # 创建并运行游戏
    game = Game()
    game.run()


if __name__ == "__main__":
    main()