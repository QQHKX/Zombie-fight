# 戴夫的炮击实验

<p align="center">
  <img src="demo.png" alt="游戏截图" width="600">
</p>

## 写在前面的话

准确的说这个是我小学六年级的参赛作品，初中的时候又重写了一下，最近闲的没事就应一些同学的需求就把这个项目开源了。现在已经完成了模块化重构，代码结构更加清晰，便于维护和扩展。

## 简介

**戴夫的炮击实验**是一款用 Python 和 Pygame 制作的简单射击游戏，灵感来源于《植物大战僵尸》。玩家将操作一门大炮，射击不断涌来的僵尸，阻止它们到达屏幕的左边缘。随着游戏进行，僵尸的速度会逐渐加快，游戏将变得越来越具有挑战性。

## 玩法

- 玩家通过鼠标控制大炮的垂直和水平位置。
- 每次点击鼠标左键，大炮会发射一枚子弹。
- 击杀僵尸后会掉落金币，可用于升级武器。
- 如果任何僵尸到达屏幕的左边缘，游戏结束。

## 游戏特点

- **无尽模式**：僵尸会不断生成，随着时间推移速度会加快，考验玩家的反应力和操作水平。
- **升级系统**：使用收集的金币升级武器伤害、射速和子弹速度。
- **多种僵尸**：游戏中有普通僵尸、快速僵尸和坦克僵尸等多种敌人。
- **粒子效果**：击中僵尸时会产生粒子效果，增强游戏打击感。
- **背景音乐**：游戏中配有背景音乐，提升游戏体验。
- **存档系统**：自动保存游戏进度和升级状态。
- **帧率显示**：可选择显示游戏帧率，帮助优化性能。
- **模块化设计**：代码结构清晰，便于扩展和维护。
  
## 安装和运行

### 系统要求

- Python 3.6 或更高版本
- Pygame 2.0.0 或更高版本

### 依赖安装

在运行游戏之前，请确保你的系统中已安装 Python 和 Pygame 库。如果尚未安装 Pygame，可以使用以下命令安装：

```bash
pip install pygame
```

### 运行游戏

1. 克隆或下载此项目代码到你的本地目录：

```bash
git clone https://github.com/你的用户名/daves-bombardment-experiment.git
cd daves-bombardment-experiment
```

2. 确保所有资源文件（如背景音乐、图片等）位于项目目录的正确位置。
3. 使用以下命令运行游戏：

```bash
python main.py
```

### 游戏控制

- **鼠标移动**：控制大炮位置
- **鼠标左键点击**：发射子弹
- **P键**：暂停/继续游戏
- **ESC键**：退出游戏

## 项目结构

```
.
├── main.py                        # 主入口文件
├── config.py                      # 游戏配置和常量
├── core/                          # 核心游戏逻辑
│   ├── __init__.py
│   ├── game.py                    # 游戏主类
│   └── resource_manager.py        # 资源管理器
├── entities/                      # 游戏实体
│   ├── __init__.py
│   ├── player.py                  # 玩家类
│   ├── bullet.py                  # 子弹类
│   ├── particle.py                # 粒子效果类
│   ├── collectibles/              # 可收集物品
│   │   ├── __init__.py
│   │   └── coin.py                # 金币类
│   └── zombies/                   # 僵尸类型
│       ├── __init__.py
│       ├── base_zombie.py         # 基础僵尸类
│       ├── normal_zombie.py       # 普通僵尸
│       ├── fast_zombie.py         # 快速僵尸
│       └── tank_zombie.py         # 坦克僵尸
├── ui/                            # 用户界面
│   ├── __init__.py
│   ├── text_renderer.py           # 文本渲染
│   ├── button.py                  # 按钮类
│   ├── hud/                       # 游戏内UI
│   │   ├── __init__.py
│   │   └── coin_display.py        # 金币显示
│   └── screens/                   # 游戏界面
│       ├── __init__.py
│       └── upgrade_menu.py        # 升级菜单
├── systems/                       # 游戏系统
│   ├── __init__.py
│   ├── economy/                   # 经济系统
│   │   ├── __init__.py
│   │   └── coin_system.py         # 金币系统
│   ├── spawner/                   # 生成系统
│   │   ├── __init__.py
│   │   └── zombie_spawner.py      # 僵尸生成器
│   ├── upgrade/                   # 升级系统
│   │   ├── __init__.py
│   │   ├── upgrade_system.py      # 升级系统
│   │   └── weapon_upgrades.py     # 武器升级
│   ├── save_manager.py            # 存档管理
│   ├── level.py                   # 关卡系统
│   └── achievement.py             # 成就系统
├── utils/                         # 工具函数
│   ├── __init__.py
│   ├── helpers.py                 # 辅助函数
│   └── logger.py                  # 日志系统
├── assets/                        # 资源文件
│   ├── images/                    # 图片资源
│   ├── sounds/                    # 音效资源
│   └── fonts/                     # 字体资源
├── logs/                          # 日志文件
├── saves/                         # 存档文件
│   └── save_data.json             # 游戏存档
└── README.md                      # 项目文档（即本文件）
```

## 开发计划

- [ ] 添加更多种类的僵尸
- [ ] 实现关卡系统
- [ ] 添加更多武器类型
- [ ] 优化游戏性能
- [ ] 添加多语言支持
- [ ] 添加音效设置选项

## 贡献指南

欢迎对本项目做出贡献！如果你想参与开发，请按照以下步骤：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 联系方式

如有任何问题或建议，请通过以下方式联系我：

- GitHub Issues: [https://github.com/你的用户名/daves-bombardment-experiment/issues](https://github.com/你的用户名/daves-bombardment-experiment/issues)
- 邮箱：你的邮箱地址

## 致谢

- 感谢 Pygame 社区提供的优秀游戏开发库
- 感谢所有为本项目做出贡献的开发者
- 背景音乐：Laura Shigihara - Zombies On Your Lawn
