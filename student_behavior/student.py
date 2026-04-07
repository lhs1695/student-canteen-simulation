"""
学生类
管理单个学生的生命周期状态和行为
"""

import threading
import time
import uuid
import random
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from .student_state import StudentState, StudentStateMachine, StateTransition


@dataclass
class StudentPreferences:
    """学生偏好配置"""
    preferred_cafeteria_id: Optional[str] = None  # 偏好食堂ID
    max_wait_time: float = 300.0  # 最大等待时间（秒）
    dining_duration_range: tuple[float, float] = (600.0, 1200.0)  # 就餐时长范围（秒）
    patience_level: float = 0.5  # 耐心水平（0.0-1.0）
    walking_speed: float = 1.0  # 行走速度（米/秒）


@dataclass
class StudentBehavior:
    """学生行为记录"""
    selected_cafeteria_id: Optional[str] = None  # 选择的食堂ID
    selected_window_id: Optional[str] = None  # 选择的窗口ID
    occupied_seat_id: Optional[str] = None  # 占用的座位ID
    queue_start_time: Optional[float] = None  # 开始排队时间
    service_start_time: Optional[float] = None  # 开始服务时间
    dining_start_time: Optional[float] = None  # 开始就餐时间


class Student:
    """
    学生类

    管理单个学生的生命周期状态和行为决策
    """

    def __init__(
        self,
        student_id: Optional[str] = None,
        preferences: Optional[StudentPreferences] = None
    ):
        """
        初始化学生

        Args:
            student_id: 学生ID，如果为None则自动生成
            preferences: 学生偏好配置
        """
        self.student_id = student_id or f"student_{uuid.uuid4().hex[:8]}"
        self.preferences = preferences or StudentPreferences()

        # 状态管理
        self._state_machine = StudentStateMachine()
        self._behavior = StudentBehavior()

        # 线程安全锁
        self._lock = threading.RLock()

        # 其他属性
        self.arrival_time = time.time()
        self.departure_time: Optional[float] = None

    # ========== 状态转换方法 ==========

    def select_cafeteria(self, cafeteria_id: str) -> bool:
        """
        选择食堂

        Args:
            cafeteria_id: 食堂ID

        Returns:
            bool: 是否成功选择
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.SELECTING_CAFETERIA):
                return False

            success = self._state_machine.transition_to(
                StudentState.SELECTING_CAFETERIA,
                trigger="cafeteria_selection",
                metadata={"cafeteria_id": cafeteria_id}
            )

            if success:
                self._behavior.selected_cafeteria_id = cafeteria_id

            return success

    def start_queuing(self, window_id: str) -> bool:
        """
        开始排队

        Args:
            window_id: 窗口ID

        Returns:
            bool: 是否成功开始排队
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.QUEUING):
                return False

            success = self._state_machine.transition_to(
                StudentState.QUEUING,
                trigger="start_queuing",
                metadata={"window_id": window_id}
            )

            if success:
                self._behavior.selected_window_id = window_id
                self._behavior.queue_start_time = time.time()

            return success

    def start_service(self) -> bool:
        """
        开始服务

        Returns:
            bool: 是否成功开始服务
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.BEING_SERVED):
                return False

            success = self._state_machine.transition_to(
                StudentState.BEING_SERVED,
                trigger="start_service",
                metadata={
                    "window_id": self._behavior.selected_window_id,
                    "wait_time": time.time() - self._behavior.queue_start_time if self._behavior.queue_start_time else 0
                }
            )

            if success:
                self._behavior.service_start_time = time.time()

            return success

    def finish_service(self) -> bool:
        """
        完成服务，开始寻找座位

        Returns:
            bool: 是否成功完成服务
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.FINDING_SEAT):
                return False

            service_duration = 0.0
            if self._behavior.service_start_time:
                service_duration = time.time() - self._behavior.service_start_time

            return self._state_machine.transition_to(
                StudentState.FINDING_SEAT,
                trigger="finish_service",
                metadata={
                    "service_duration": service_duration,
                    "window_id": self._behavior.selected_window_id
                }
            )

    def find_seat(self, seat_id: str) -> bool:
        """
        找到座位，开始就餐

        Args:
            seat_id: 座位ID

        Returns:
            bool: 是否成功找到座位
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.DINING):
                return False

            success = self._state_machine.transition_to(
                StudentState.DINING,
                trigger="find_seat",
                metadata={"seat_id": seat_id}
            )

            if success:
                self._behavior.occupied_seat_id = seat_id
                self._behavior.dining_start_time = time.time()

            return success

    def start_leaving(self) -> bool:
        """
        开始离开

        Returns:
            bool: 是否成功开始离开
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.LEAVING):
                return False

            metadata = {}
            if self._behavior.dining_start_time:
                metadata["dining_duration"] = time.time() - self._behavior.dining_start_time

            return self._state_machine.transition_to(
                StudentState.LEAVING,
                trigger="start_leaving",
                metadata=metadata
            )

    def complete_leaving(self) -> bool:
        """
        完成离开

        Returns:
            bool: 是否成功离开系统
        """
        with self._lock:
            if not self._state_machine.can_transition_to(StudentState.LEFT):
                return False

            success = self._state_machine.transition_to(
                StudentState.LEFT,
                trigger="complete_leaving",
                metadata={"total_time": time.time() - self.arrival_time}
            )

            if success:
                self.departure_time = time.time()

            return success

    def abandon_queue(self) -> bool:
        """
        放弃排队

        Returns:
            bool: 是否成功放弃
        """
        with self._lock:
            if self._state_machine.get_current_state() not in [StudentState.QUEUING, StudentState.BEING_SERVED]:
                return False

            wait_time = 0.0
            if self._behavior.queue_start_time:
                wait_time = time.time() - self._behavior.queue_start_time

            return self._state_machine.transition_to(
                StudentState.LEAVING,
                trigger="abandon_queue",
                metadata={
                    "wait_time": wait_time,
                    "reason": "impatient"
                }
            )

    # ========== 查询方法 ==========

    def get_current_state(self) -> StudentState:
        """获取当前状态"""
        with self._lock:
            return self._state_machine.get_current_state()

    def get_behavior_info(self) -> StudentBehavior:
        """获取行为信息（返回副本）"""
        with self._lock:
            return StudentBehavior(
                selected_cafeteria_id=self._behavior.selected_cafeteria_id,
                selected_window_id=self._behavior.selected_window_id,
                occupied_seat_id=self._behavior.occupied_seat_id,
                queue_start_time=self._behavior.queue_start_time,
                service_start_time=self._behavior.service_start_time,
                dining_start_time=self._behavior.dining_start_time
            )

    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        with self._lock:
            state_summary = self._state_machine.get_state_summary()
            behavior = self.get_behavior_info()

            return {
                "student_id": self.student_id,
                "arrival_time": self.arrival_time,
                "departure_time": self.departure_time,
                "total_time_in_system": time.time() - self.arrival_time if not self.departure_time else self.departure_time - self.arrival_time,
                **state_summary,
                "preferences": {
                    "preferred_cafeteria_id": self.preferences.preferred_cafeteria_id,
                    "max_wait_time": self.preferences.max_wait_time,
                    "dining_duration_range": self.preferences.dining_duration_range,
                    "patience_level": self.preferences.patience_level,
                    "walking_speed": self.preferences.walking_speed
                },
                "behavior": {
                    "selected_cafeteria_id": behavior.selected_cafeteria_id,
                    "selected_window_id": behavior.selected_window_id,
                    "occupied_seat_id": behavior.occupied_seat_id,
                    "current_wait_time": time.time() - behavior.queue_start_time if behavior.queue_start_time and self.get_current_state() in [StudentState.QUEUING, StudentState.BEING_SERVED] else None,
                    "current_service_time": time.time() - behavior.service_start_time if behavior.service_start_time and self.get_current_state() == StudentState.BEING_SERVED else None,
                    "current_dining_time": time.time() - behavior.dining_start_time if behavior.dining_start_time and self.get_current_state() == StudentState.DINING else None
                }
            }

    def get_transition_history(self) -> List[StateTransition]:
        """获取状态转换历史"""
        with self._lock:
            return self._state_machine.get_transition_history()

    def is_waiting_too_long(self) -> bool:
        """
        检查是否等待时间过长（超过最大等待时间）

        Returns:
            bool: 是否等待时间过长
        """
        with self._lock:
            current_state = self.get_current_state()
            if current_state not in [StudentState.QUEUING, StudentState.BEING_SERVED]:
                return False

            if not self._behavior.queue_start_time:
                return False

            wait_time = time.time() - self._behavior.queue_start_time
            patience_adjusted_max_wait = self.preferences.max_wait_time * self.preferences.patience_level

            return wait_time > patience_adjusted_max_wait

    def get_estimated_dining_duration(self) -> float:
        """
        获取预计就餐时长

        Returns:
            float: 预计就餐时长（秒）
        """
        with self._lock:
            # 基于偏好范围随机生成就餐时长
            min_duration, max_duration = self.preferences.dining_duration_range
            return random.uniform(min_duration, max_duration)

    def should_abandon(self) -> bool:
        """
        判断是否应该放弃（基于耐心水平和等待时间）

        Returns:
            bool: 是否应该放弃
        """
        with self._lock:
            return self.is_waiting_too_long()

    def reset(self, new_preferences: Optional[StudentPreferences] = None) -> None:
        """
        重置学生状态

        Args:
            new_preferences: 新的偏好配置，如果为None则保持原有配置
        """
        with self._lock:
            self._state_machine.reset()
            self._behavior = StudentBehavior()
            self.arrival_time = time.time()
            self.departure_time = None

            if new_preferences:
                self.preferences = new_preferences