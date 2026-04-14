"""
服务窗口模块
管理单个服务窗口的队列和服务状态
"""

import threading
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class WindowStatus(Enum):
    """窗口状态枚举"""
    IDLE = "idle"  # 空闲
    SERVING = "serving"  # 服务中
    CLOSED = "closed"  # 已关闭


@dataclass
class ServiceStats:
    """服务统计信息"""
    total_served: int = 0  # 总服务人数
    total_service_time: float = 0.0  # 总服务时间（秒）
    max_queue_length: int = 0  # 最大队列长度
    current_queue_length: int = 0  # 当前队列长度

    @property
    def avg_service_time(self) -> float:
        """平均服务时间"""
        return self.total_service_time / self.total_served if self.total_served > 0 else 0.0


class ServiceWindow:
    """
    服务窗口类

    管理单个窗口的队列和服务状态，支持线程安全操作
    """

    def __init__(self, window_id: str, cafeteria_id: str, service_rate: float = 1.0):
        """
        初始化服务窗口

        Args:
            window_id: 窗口唯一标识符
            cafeteria_id: 所属食堂ID
            service_rate: 服务速率（人/秒），默认1.0
        """
        self.window_id = window_id
        self.cafeteria_id = cafeteria_id
        self.service_rate = service_rate

        # 窗口状态
        self._status = WindowStatus.IDLE
        self._current_student_id: Optional[str] = None
        self._service_start_time: Optional[float] = None

        # 队列管理（使用列表实现FIFO队列）
        self._queue: List[str] = []  # 存储学生ID

        # 统计信息
        self._stats = ServiceStats()

        # 线程安全锁
        self._lock = threading.RLock()

        # 配置参数
        self.max_queue_capacity = 100  # 最大队列容量

    def enqueue_student(self, student_id: str) -> bool:
        """
        学生加入队列

        Args:
            student_id: 学生ID

        Returns:
            bool: 是否成功加入队列
        """
        with self._lock:
            if len(self._queue) >= self.max_queue_capacity:
                return False

            self._queue.append(student_id)
            self._stats.current_queue_length = len(self._queue)
            self._stats.max_queue_length = max(
                self._stats.max_queue_length,
                self._stats.current_queue_length
            )
            return True

    def dequeue_student(self) -> Optional[str]:
        """
        从队列中取出下一个学生

        Returns:
            Optional[str]: 学生ID，如果队列为空则返回None
        """
        with self._lock:
            if not self._queue:
                return None

            student_id = self._queue.pop(0)
            self._stats.current_queue_length = len(self._queue)
            return student_id

    def start_service(self) -> bool:
        """
        开始为下一个学生服务（从队列中取出）

        Returns:
            bool: 是否成功开始服务
        """
        with self._lock:
            if self._status != WindowStatus.IDLE:
                return False

            # 从队列中取出下一个学生
            student_id = self.dequeue_student()
            if student_id is None:
                return False

            self._status = WindowStatus.SERVING
            self._current_student_id = student_id
            self._service_start_time = time.time()
            return True

    def complete_service(self) -> Optional[str]:
        """
        完成当前服务

        Returns:
            Optional[str]: 被服务的学生ID，如果当前没有服务则返回None
        """
        with self._lock:
            if self._status != WindowStatus.SERVING:
                return None

            student_id = self._current_student_id
            service_time = time.time() - self._service_start_time # type: ignore

            # 更新统计信息
            self._stats.total_served += 1
            self._stats.total_service_time += service_time

            # 重置状态
            self._status = WindowStatus.IDLE
            self._current_student_id = None
            self._service_start_time = None

            return student_id

    def close_window(self) -> bool:
        """
        关闭窗口

        Returns:
            bool: 是否成功关闭
        """
        with self._lock:
            if self._status == WindowStatus.CLOSED:
                return False

            self._status = WindowStatus.CLOSED
            self._current_student_id = None
            self._service_start_time = None
            return True

    def open_window(self) -> bool:
        """
        打开窗口

        Returns:
            bool: 是否成功打开
        """
        with self._lock:
            if self._status != WindowStatus.CLOSED:
                return False

            self._status = WindowStatus.IDLE
            return True

    def get_queue_length(self) -> int:
        """获取当前队列长度"""
        with self._lock:
            return len(self._queue)

    def get_estimated_wait_time(self) -> float:
        """
        获取预计等待时间

        Returns:
            float: 预计等待时间（秒）
        """
        with self._lock:
            queue_length = len(self._queue)

            if self._status == WindowStatus.SERVING:
                # 计算当前服务的剩余时间
                current_service_time = time.time() - self._service_start_time # type: ignore
                remaining_service_time = max(0, (1.0 / self.service_rate) - current_service_time)
            else:
                # 窗口空闲，没有当前服务
                remaining_service_time = 0.0

            # 队列中所有学生的服务时间
            queue_service_time = queue_length * (1.0 / self.service_rate)

            return remaining_service_time + queue_service_time

    def get_status(self) -> WindowStatus:
        """获取窗口状态"""
        with self._lock:
            return self._status

    def get_current_student(self) -> Optional[str]:
        """获取当前正在服务的学生ID"""
        with self._lock:
            return self._current_student_id

    def get_stats(self) -> ServiceStats:
        """获取统计信息（返回副本）"""
        with self._lock:
            return ServiceStats(
                total_served=self._stats.total_served,
                total_service_time=self._stats.total_service_time,
                max_queue_length=self._stats.max_queue_length,
                current_queue_length=self._stats.current_queue_length
            )

    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口完整信息"""
        with self._lock:
            return {
                "window_id": self.window_id,
                "cafeteria_id": self.cafeteria_id,
                "status": self._status.value,
                "current_student": self._current_student_id,
                "queue_length": len(self._queue),
                "queue": self._queue.copy(),
                "service_rate": self.service_rate,
                "estimated_wait_time": self.get_estimated_wait_time(),
                "stats": {
                    "total_served": self._stats.total_served,
                    "total_service_time": self._stats.total_service_time,
                    "avg_service_time": self._stats.avg_service_time,
                    "max_queue_length": self._stats.max_queue_length,
                    "current_queue_length": self._stats.current_queue_length
                }
            }

    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            # 保存当前队列长度
            current_queue_len = len(self._queue)
            # 创建新的统计对象
            self._stats = ServiceStats()
            # 设置当前队列长度
            self._stats.current_queue_length = current_queue_len
            # 注意：不清除队列和当前状态，只重置统计