"""
学生状态模块
定义学生的状态枚举和状态转换逻辑
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time


class StudentState(Enum):
    """
    学生状态枚举

    定义了学生在食堂仿真系统中的完整生命周期状态
    """
    ARRIVED = "arrived"  # 到达系统
    SELECTING_CAFETERIA = "selecting_cafeteria"  # 选择食堂
    QUEUING = "queuing"  # 排队中
    BEING_SERVED = "being_served"  # 服务中
    FINDING_SEAT = "finding_seat"  # 寻找座位
    DINING = "dining"  # 就餐中
    LEAVING = "leaving"  # 离开中
    LEFT = "left"  # 已离开系统


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: StudentState
    to_state: StudentState
    timestamp: float
    trigger: str  # 转换触发原因
    metadata: Optional[Dict[str, Any]] = None


class StudentStateMachine:
    """
    学生状态机

    管理学生的状态转换和状态历史
    """

    def __init__(self, initial_state: StudentState = StudentState.ARRIVED):
        """
        初始化状态机

        Args:
            initial_state: 初始状态
        """
        self._current_state = initial_state
        self._state_start_time = time.time()
        self._transition_history: List[StateTransition] = []
        self._state_durations: Dict[StudentState, float] = {state: 0.0 for state in StudentState}

        # 记录初始状态
        self._transition_history.append(StateTransition(
            from_state=initial_state,
            to_state=initial_state,
            timestamp=self._state_start_time,
            trigger="initialization"
        ))

    def transition_to(self, new_state: StudentState, trigger: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        转换到新状态

        Args:
            new_state: 新状态
            trigger: 转换触发原因
            metadata: 附加元数据

        Returns:
            bool: 是否成功转换
        """
        # 检查状态转换是否有效
        if not self._is_valid_transition(self._current_state, new_state):
            return False

        # 计算当前状态的持续时间
        current_duration = time.time() - self._state_start_time
        self._state_durations[self._current_state] = self._state_durations.get(self._current_state, 0.0) + current_duration

        # 记录状态转换
        transition = StateTransition(
            from_state=self._current_state,
            to_state=new_state,
            timestamp=time.time(),
            trigger=trigger,
            metadata=metadata
        )
        self._transition_history.append(transition)

        # 更新当前状态
        old_state = self._current_state
        self._current_state = new_state
        self._state_start_time = time.time()

        return True

    def _is_valid_transition(self, from_state: StudentState, to_state: StudentState) -> bool:
        """
        检查状态转换是否有效

        Args:
            from_state: 起始状态
            to_state: 目标状态

        Returns:
            bool: 转换是否有效
        """
        # 定义有效的状态转换规则
        valid_transitions = {
            StudentState.ARRIVED: [StudentState.SELECTING_CAFETERIA],
            StudentState.SELECTING_CAFETERIA: [StudentState.QUEUING, StudentState.LEAVING],
            StudentState.QUEUING: [StudentState.BEING_SERVED, StudentState.LEAVING],
            StudentState.BEING_SERVED: [StudentState.FINDING_SEAT, StudentState.LEAVING],
            StudentState.FINDING_SEAT: [StudentState.DINING, StudentState.LEAVING],
            StudentState.DINING: [StudentState.LEAVING],
            StudentState.LEAVING: [StudentState.LEFT],
            StudentState.LEFT: []  # 最终状态，不能转换到其他状态
        }

        return to_state in valid_transitions.get(from_state, [])

    def get_current_state(self) -> StudentState:
        """获取当前状态"""
        return self._current_state

    def get_current_state_duration(self) -> float:
        """获取当前状态的持续时间（秒）"""
        return time.time() - self._state_start_time

    def get_state_duration(self, state: StudentState) -> float:
        """获取特定状态的总持续时间（秒）"""
        return self._state_durations.get(state, 0.0)

    def get_transition_history(self) -> List[StateTransition]:
        """获取状态转换历史"""
        return self._transition_history.copy()

    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            "current_state": self._current_state.value,
            "current_state_duration": self.get_current_state_duration(),
            "state_durations": {state.value: duration for state, duration in self._state_durations.items()},
            "total_transitions": len(self._transition_history) - 1,  # 减去初始状态
            "is_final_state": self._current_state == StudentState.LEFT
        }

    def can_transition_to(self, target_state: StudentState) -> bool:
        """检查是否可以转换到目标状态"""
        return self._is_valid_transition(self._current_state, target_state)

    def reset(self, initial_state: StudentState = StudentState.ARRIVED) -> None:
        """重置状态机"""
        self._current_state = initial_state
        self._state_start_time = time.time()
        self._transition_history.clear()
        self._state_durations.clear()

        # 重新初始化状态持续时间字典
        self._state_durations = {state: 0.0 for state in StudentState}

        # 记录初始状态
        self._transition_history.append(StateTransition(
            from_state=initial_state,
            to_state=initial_state,
            timestamp=self._state_start_time,
            trigger="reset"
        ))