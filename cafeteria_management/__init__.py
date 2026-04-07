"""
食堂管理模块
管理多个食堂及其内部资源状态
"""

from .service_window import ServiceWindow, WindowStatus, ServiceStats
from .cafeteria import Cafeteria, Seat, CafeteriaStats
from .manager import CafeteriaManager

__version__ = "1.0.0"
__all__ = [
    "ServiceWindow",
    "WindowStatus",
    "ServiceStats",
    "Cafeteria",
    "Seat",
    "CafeteriaStats",
    "CafeteriaManager"
]