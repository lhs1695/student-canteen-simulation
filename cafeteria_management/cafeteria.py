"""
食堂模块
管理单个食堂的窗口和座位资源
"""

import threading
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from .service_window import ServiceWindow, WindowStatus


@dataclass
class Seat:
    """座位类"""
    seat_id: str
    cafeteria_id: str
    is_occupied: bool = False
    occupied_by: Optional[str] = None  # 被哪个学生占用
    occupied_since: Optional[float] = None  # 占用开始时间


@dataclass
class CafeteriaStats:
    """食堂统计信息"""
    total_students_served: int = 0
    total_seats_utilization: float = 0.0  # 总座位利用率
    peak_occupancy: int = 0  # 峰值占用人数
    current_occupancy: int = 0  # 当前占用人数


class Cafeteria:
    """
    食堂类

    管理单个食堂的窗口和座位资源
    """

    def __init__(self, cafeteria_id: str, name: str, total_seats: int):
        """
        初始化食堂

        Args:
            cafeteria_id: 食堂唯一标识符
            name: 食堂名称
            total_seats: 总座位数
        """
        self.cafeteria_id = cafeteria_id
        self.name = name
        self.total_seats = total_seats

        # 窗口管理
        self._windows: Dict[str, ServiceWindow] = {}
        self._window_ids: List[str] = []  # 保持插入顺序

        # 座位管理
        self._seats: Dict[str, Seat] = {}
        self._initialize_seats(total_seats)

        # 统计信息
        self._stats = CafeteriaStats()

        # 线程安全锁
        self._lock = threading.RLock()

    def _initialize_seats(self, total_seats: int) -> None:
        """初始化座位"""
        for i in range(total_seats):
            seat_id = f"seat_{self.cafeteria_id}_{i:04d}"
            self._seats[seat_id] = Seat(seat_id=seat_id, cafeteria_id=self.cafeteria_id)

    def add_window(self, window_id: str, service_rate: float = 1.0) -> bool:
        """
        添加服务窗口

        Args:
            window_id: 窗口ID
            service_rate: 服务速率

        Returns:
            bool: 是否成功添加
        """
        with self._lock:
            if window_id in self._windows:
                return False

            window = ServiceWindow(window_id, self.cafeteria_id, service_rate)
            self._windows[window_id] = window
            self._window_ids.append(window_id)
            return True

    def remove_window(self, window_id: str) -> bool:
        """
        移除服务窗口

        Args:
            window_id: 窗口ID

        Returns:
            bool: 是否成功移除
        """
        with self._lock:
            if window_id not in self._windows:
                return False

            del self._windows[window_id]
            self._window_ids.remove(window_id)
            return True

    def get_window(self, window_id: str) -> Optional[ServiceWindow]:
        """获取指定窗口"""
        with self._lock:
            return self._windows.get(window_id)

    def get_all_windows(self) -> List[ServiceWindow]:
        """获取所有窗口（按添加顺序）"""
        with self._lock:
            return [self._windows[wid] for wid in self._window_ids]

    def get_available_windows(self) -> List[ServiceWindow]:
        """获取所有可用的窗口（非关闭状态）"""
        with self._lock:
            return [
                window for window in self._windows.values()
                if window.get_status() != WindowStatus.CLOSED
            ]

    def find_best_window(self) -> Optional[ServiceWindow]:
        """
        寻找最佳窗口（队列最短的窗口）

        Returns:
            Optional[ServiceWindow]: 最佳窗口，如果没有可用窗口则返回None
        """
        with self._lock:
            available_windows = self.get_available_windows()
            if not available_windows:
                return None

            # 选择队列最短的窗口
            best_window = min(
                available_windows,
                key=lambda w: w.get_queue_length()
            )
            return best_window

    def occupy_seat(self, student_id: str) -> Optional[str]:
        """
        占用一个空闲座位

        Args:
            student_id: 学生ID

        Returns:
            Optional[str]: 座位ID，如果没有空闲座位则返回None
        """
        with self._lock:
            for seat in self._seats.values():
                if not seat.is_occupied:
                    seat.is_occupied = True
                    seat.occupied_by = student_id
                    seat.occupied_since = threading.get_ident()  # 临时使用线程ID作为时间戳

                    # 更新统计
                    self._stats.current_occupancy += 1
                    self._stats.peak_occupancy = max(
                        self._stats.peak_occupancy,
                        self._stats.current_occupancy
                    )

                    return seat.seat_id
            return None

    def release_seat(self, seat_id: str) -> bool:
        """
        释放座位

        Args:
            seat_id: 座位ID

        Returns:
            bool: 是否成功释放
        """
        with self._lock:
            if seat_id not in self._seats:
                return False

            seat = self._seats[seat_id]
            if not seat.is_occupied:
                return False

            seat.is_occupied = False
            seat.occupied_by = None
            seat.occupied_since = None

            # 更新统计
            self._stats.current_occupancy -= 1
            self._stats.total_students_served += 1

            return True

    def get_available_seats_count(self) -> int:
        """获取可用座位数"""
        with self._lock:
            return sum(1 for seat in self._seats.values() if not seat.is_occupied)

    def get_occupied_seats(self) -> List[Seat]:
        """获取被占用的座位列表"""
        with self._lock:
            return [seat for seat in self._seats.values() if seat.is_occupied]

    def get_seat_info(self, seat_id: str) -> Optional[Dict[str, Any]]:
        """获取座位信息"""
        with self._lock:
            seat = self._seats.get(seat_id)
            if not seat:
                return None

            return {
                "seat_id": seat.seat_id,
                "cafeteria_id": seat.cafeteria_id,
                "is_occupied": seat.is_occupied,
                "occupied_by": seat.occupied_by,
                "occupied_since": seat.occupied_since
            }

    def get_cafeteria_stats(self) -> CafeteriaStats:
        """获取食堂统计信息（返回副本）"""
        with self._lock:
            # 计算座位利用率
            if self.total_seats > 0:
                utilization = (self._stats.current_occupancy / self.total_seats) * 100
            else:
                utilization = 0.0

            return CafeteriaStats(
                total_students_served=self._stats.total_students_served,
                total_seats_utilization=utilization,
                peak_occupancy=self._stats.peak_occupancy,
                current_occupancy=self._stats.current_occupancy
            )

    def get_cafeteria_info(self) -> Dict[str, Any]:
        """获取食堂完整信息"""
        with self._lock:
            windows_info = []
            for window_id in self._window_ids:
                window = self._windows[window_id]
                windows_info.append(window.get_window_info())

            seats_info = []
            for seat in self._seats.values():
                seats_info.append({
                    "seat_id": seat.seat_id,
                    "is_occupied": seat.is_occupied,
                    "occupied_by": seat.occupied_by
                })

            stats = self.get_cafeteria_stats()

            return {
                "cafeteria_id": self.cafeteria_id,
                "name": self.name,
                "total_seats": self.total_seats,
                "available_seats": self.get_available_seats_count(),
                "current_occupancy": stats.current_occupancy,
                "peak_occupancy": stats.peak_occupancy,
                "seat_utilization": stats.total_seats_utilization,
                "total_students_served": stats.total_students_served,
                "windows_count": len(self._windows),
                "windows": windows_info,
                "seats": seats_info
            }

    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            # 保存当前占用状态
            current_occupancy = self._stats.current_occupancy
            # 创建新的统计对象
            self._stats = CafeteriaStats()
            # 重置后，当前占用保持不变，峰值占用设置为当前占用
            self._stats.current_occupancy = current_occupancy
            self._stats.peak_occupancy = current_occupancy
            # 重置所有窗口的统计
            for window in self._windows.values():
                window.reset_stats()