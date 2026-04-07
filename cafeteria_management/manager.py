"""
食堂管理器模块
管理多个食堂的创建、查询和资源分配
"""

import threading
from typing import Dict, List, Optional, Any
from .cafeteria import Cafeteria


class CafeteriaManager:
    """
    食堂管理器类

    管理多个食堂，提供统一的资源分配和状态查询接口
    """

    def __init__(self):
        """初始化食堂管理器"""
        self._cafeterias: Dict[str, Cafeteria] = {}
        self._cafeteria_ids: List[str] = []  # 保持插入顺序
        self._lock = threading.RLock()

    def create_cafeteria(self, cafeteria_id: str, name: str, total_seats: int) -> bool:
        """
        创建新食堂

        Args:
            cafeteria_id: 食堂唯一标识符
            name: 食堂名称
            total_seats: 总座位数

        Returns:
            bool: 是否成功创建
        """
        with self._lock:
            if cafeteria_id in self._cafeterias:
                return False

            cafeteria = Cafeteria(cafeteria_id, name, total_seats)
            self._cafeterias[cafeteria_id] = cafeteria
            self._cafeteria_ids.append(cafeteria_id)
            return True

    def remove_cafeteria(self, cafeteria_id: str) -> bool:
        """
        移除食堂

        Args:
            cafeteria_id: 食堂ID

        Returns:
            bool: 是否成功移除
        """
        with self._lock:
            if cafeteria_id not in self._cafeterias:
                return False

            del self._cafeterias[cafeteria_id]
            self._cafeteria_ids.remove(cafeteria_id)
            return True

    def get_cafeteria(self, cafeteria_id: str) -> Optional[Cafeteria]:
        """获取指定食堂"""
        with self._lock:
            return self._cafeterias.get(cafeteria_id)

    def get_all_cafeterias(self) -> List[Cafeteria]:
        """获取所有食堂（按创建顺序）"""
        with self._lock:
            return [self._cafeterias[cid] for cid in self._cafeteria_ids]

    def get_cafeteria_info(self, cafeteria_id: str) -> Optional[Dict[str, Any]]:
        """获取食堂信息"""
        with self._lock:
            cafeteria = self._cafeterias.get(cafeteria_id)
            if not cafeteria:
                return None

            return cafeteria.get_cafeteria_info()

    def get_all_cafeterias_info(self) -> List[Dict[str, Any]]:
        """获取所有食堂信息"""
        with self._lock:
            return [
                cafeteria.get_cafeteria_info()
                for cafeteria in self._cafeterias.values()
            ]

    def find_best_cafeteria(self, preference: Optional[str] = None) -> Optional[str]:
        """
        寻找最佳食堂

        Args:
            preference: 偏好食堂ID，如果指定则优先返回该食堂（如果可用）

        Returns:
            Optional[str]: 最佳食堂ID，如果没有可用食堂则返回None
        """
        with self._lock:
            # 如果有偏好食堂且该食堂存在
            if preference and preference in self._cafeterias:
                cafeteria = self._cafeterias[preference]
                if cafeteria.get_available_seats_count() > 0:
                    return preference

            # 否则寻找可用座位最多的食堂
            best_cafeteria_id = None
            max_available_seats = -1

            for cafeteria_id, cafeteria in self._cafeterias.items():
                available_seats = cafeteria.get_available_seats_count()
                if available_seats > max_available_seats:
                    max_available_seats = available_seats
                    best_cafeteria_id = cafeteria_id

            return best_cafeteria_id if max_available_seats > 0 else None

    def allocate_window(self, cafeteria_id: str) -> Optional[str]:
        """
        在指定食堂分配最佳窗口

        Args:
            cafeteria_id: 食堂ID

        Returns:
            Optional[str]: 窗口ID，如果食堂不存在或没有可用窗口则返回None
        """
        with self._lock:
            cafeteria = self._cafeterias.get(cafeteria_id)
            if not cafeteria:
                return None

            best_window = cafeteria.find_best_window()
            return best_window.window_id if best_window else None

    def occupy_seat(self, cafeteria_id: str, student_id: str) -> Optional[str]:
        """
        在指定食堂占用座位

        Args:
            cafeteria_id: 食堂ID
            student_id: 学生ID

        Returns:
            Optional[str]: 座位ID，如果食堂不存在或没有空闲座位则返回None
        """
        with self._lock:
            cafeteria = self._cafeterias.get(cafeteria_id)
            if not cafeteria:
                return None

            return cafeteria.occupy_seat(student_id)

    def release_seat(self, cafeteria_id: str, seat_id: str) -> bool:
        """
        在指定食堂释放座位

        Args:
            cafeteria_id: 食堂ID
            seat_id: 座位ID

        Returns:
            bool: 是否成功释放
        """
        with self._lock:
            cafeteria = self._cafeterias.get(cafeteria_id)
            if not cafeteria:
                return False

            return cafeteria.release_seat(seat_id)

    def add_window_to_cafeteria(
        self,
        cafeteria_id: str,
        window_id: str,
        service_rate: float = 1.0
    ) -> bool:
        """
        为食堂添加窗口

        Args:
            cafeteria_id: 食堂ID
            window_id: 窗口ID
            service_rate: 服务速率

        Returns:
            bool: 是否成功添加
        """
        with self._lock:
            cafeteria = self._cafeterias.get(cafeteria_id)
            if not cafeteria:
                return False

            return cafeteria.add_window(window_id, service_rate)

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统整体统计信息"""
        with self._lock:
            total_cafeterias = len(self._cafeterias)
            total_windows = 0
            total_seats = 0
            total_available_seats = 0
            total_occupied_seats = 0
            total_students_served = 0

            for cafeteria in self._cafeterias.values():
                cafeteria_info = cafeteria.get_cafeteria_info()
                total_windows += cafeteria_info["windows_count"]
                total_seats += cafeteria_info["total_seats"]
                total_available_seats += cafeteria_info["available_seats"]
                total_occupied_seats += cafeteria_info["current_occupancy"]
                total_students_served += cafeteria_info["total_students_served"]

            return {
                "total_cafeterias": total_cafeterias,
                "total_windows": total_windows,
                "total_seats": total_seats,
                "total_available_seats": total_available_seats,
                "total_occupied_seats": total_occupied_seats,
                "seat_utilization_rate": (total_occupied_seats / total_seats * 100) if total_seats > 0 else 0,
                "total_students_served": total_students_served
            }

    def clear_all(self) -> None:
        """清空所有食堂（用于重置系统）"""
        with self._lock:
            self._cafeterias.clear()
            self._cafeteria_ids.clear()