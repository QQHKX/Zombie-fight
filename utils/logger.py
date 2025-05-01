import os
import logging
import datetime
import traceback
from enum import Enum, auto

# 定义事件类型枚举
class EventType(Enum):
    """事件类型枚举，用于分类不同的日志事件"""
    SYSTEM = auto()       # 系统事件（如游戏启动、关闭等）
    PLAYER = auto()       # 玩家事件（如玩家移动、射击等）
    ZOMBIE = auto()       # 僵尸事件（如僵尸生成、死亡等）
    COLLISION = auto()    # 碰撞事件（如子弹击中僵尸等）
    GAME_STATE = auto()   # 游戏状态事件（如游戏开始、暂停、结束等）
    RESOURCE = auto()     # 资源事件（如资源加载、释放等）
    ECONOMY = auto()      # 经济事件（如金币获取、消费等）
    UPGRADE = auto()      # 升级事件（如武器升级等）
    SAVE = auto()         # 存档事件（如存档加载、保存等）
    ERROR = auto()        # 错误事件（如异常、错误等）
    DEBUG = auto()        # 调试事件（用于开发调试）

class GameLogger:
    """游戏日志系统，提供全局日志记录功能"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式，确保只有一个日志实例"""
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化日志系统"""
        if self._initialized:
            return
        
        # 创建日志目录
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 获取当前日期作为日志文件名
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"game_{current_date}.log")
        
        # 配置日志格式
        self.logger = logging.getLogger("GameLogger")
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(event_type)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 事件类型过滤器
        self.event_filters = set()
        
        # 标记为已初始化
        self._initialized = True
        
        # 记录日志系统启动
        self.log(EventType.SYSTEM, "日志系统初始化完成")
    
    def log(self, event_type, message, level=logging.INFO, **kwargs):
        """记录日志
        
        Args:
            event_type: 事件类型，使用EventType枚举
            message: 日志消息
            level: 日志级别，默认为INFO
            **kwargs: 额外的日志信息，将以键值对形式添加到日志中
        """
        # 检查事件过滤
        if self.event_filters and event_type not in self.event_filters:
            return
        
        # 构建额外信息
        extra = {"event_type": event_type.name}
        
        # 添加额外的键值对到日志消息
        if kwargs:
            details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} - {details}"
        
        # 根据级别记录日志
        if level == logging.DEBUG:
            self.logger.debug(message, extra=extra)
        elif level == logging.INFO:
            self.logger.info(message, extra=extra)
        elif level == logging.WARNING:
            self.logger.warning(message, extra=extra)
        elif level == logging.ERROR:
            self.logger.error(message, extra=extra)
        elif level == logging.CRITICAL:
            self.logger.critical(message, extra=extra)
    
    def debug(self, event_type, message, **kwargs):
        """记录调试级别日志"""
        self.log(event_type, message, logging.DEBUG, **kwargs)
    
    def info(self, event_type, message, **kwargs):
        """记录信息级别日志"""
        self.log(event_type, message, logging.INFO, **kwargs)
    
    def warning(self, event_type, message, **kwargs):
        """记录警告级别日志"""
        self.log(event_type, message, logging.WARNING, **kwargs)
    
    def error(self, event_type, message, **kwargs):
        """记录错误级别日志"""
        self.log(event_type, message, logging.ERROR, **kwargs)
    
    def critical(self, event_type, message, **kwargs):
        """记录严重错误级别日志"""
        self.log(event_type, message, logging.CRITICAL, **kwargs)
    
    def exception(self, event_type, message, exc_info=True, **kwargs):
        """记录异常信息
        
        Args:
            event_type: 事件类型
            message: 日志消息
            exc_info: 是否包含异常信息，默认为True
            **kwargs: 额外的日志信息
        """
        # 获取异常堆栈信息
        if exc_info:
            stack_trace = traceback.format_exc()
            message = f"{message}\n{stack_trace}"
        
        self.log(event_type, message, logging.ERROR, **kwargs)
    
    def set_event_filters(self, event_types):
        """设置事件类型过滤器，只记录指定类型的事件
        
        Args:
            event_types: EventType枚举列表，只记录这些类型的事件
        """
        self.event_filters = set(event_types)
    
    def clear_event_filters(self):
        """清除事件类型过滤器，记录所有类型的事件"""
        self.event_filters.clear()

# 创建全局日志实例
game_logger = GameLogger()

# 简化的日志接口函数
def log_system(message, level=logging.INFO, **kwargs):
    """记录系统事件"""
    game_logger.log(EventType.SYSTEM, message, level, **kwargs)

def log_player(message, level=logging.INFO, **kwargs):
    """记录玩家事件"""
    game_logger.log(EventType.PLAYER, message, level, **kwargs)

def log_zombie(message, level=logging.INFO, **kwargs):
    """记录僵尸事件"""
    game_logger.log(EventType.ZOMBIE, message, level, **kwargs)

def log_collision(message, level=logging.INFO, **kwargs):
    """记录碰撞事件"""
    game_logger.log(EventType.COLLISION, message, level, **kwargs)

def log_game_state(message, level=logging.INFO, **kwargs):
    """记录游戏状态事件"""
    game_logger.log(EventType.GAME_STATE, message, level, **kwargs)

def log_resource(message, level=logging.INFO, **kwargs):
    """记录资源事件"""
    game_logger.log(EventType.RESOURCE, message, level, **kwargs)

def log_economy(message, level=logging.INFO, **kwargs):
    """记录经济事件"""
    game_logger.log(EventType.ECONOMY, message, level, **kwargs)

def log_upgrade(message, level=logging.INFO, **kwargs):
    """记录升级事件"""
    game_logger.log(EventType.UPGRADE, message, level, **kwargs)

def log_save(message, level=logging.INFO, **kwargs):
    """记录存档事件"""
    game_logger.log(EventType.SAVE, message, level, **kwargs)

def log_error(message, **kwargs):
    """记录错误事件"""
    game_logger.log(EventType.ERROR, message, logging.ERROR, **kwargs)

def log_debug(message, **kwargs):
    """记录调试事件"""
    game_logger.log(EventType.DEBUG, message, logging.DEBUG, **kwargs)

def log_exception(message, exc_info=True, **kwargs):
    """记录异常信息"""
    game_logger.exception(EventType.ERROR, message, exc_info, **kwargs)