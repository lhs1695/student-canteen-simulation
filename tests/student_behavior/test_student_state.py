"""
学生状态机单元测试
"""

import time
import pytest
from student_behavior.student_state import StudentState, StudentStateMachine, StateTransition


class TestStudentStateMachine:
    """学生状态机测试类"""

    def test_initialization(self):
        """测试初始化"""
        # 默认初始状态
        state_machine = StudentStateMachine()
        assert state_machine.get_current_state() == StudentState.ARRIVED

        # 指定初始状态
        state_machine = StudentStateMachine(StudentState.QUEUING)
        assert state_machine.get_current_state() == StudentState.QUEUING

    def test_valid_transitions(self):
        """测试有效状态转换"""
        state_machine = StudentStateMachine()

        # ARRIVED -> SELECTING_CAFETERIA
        assert state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test") is True
        assert state_machine.get_current_state() == StudentState.SELECTING_CAFETERIA

        # SELECTING_CAFETERIA -> QUEUING
        assert state_machine.transition_to(StudentState.QUEUING, "test") is True
        assert state_machine.get_current_state() == StudentState.QUEUING

        # QUEUING -> BEING_SERVED
        assert state_machine.transition_to(StudentState.BEING_SERVED, "test") is True
        assert state_machine.get_current_state() == StudentState.BEING_SERVED

        # BEING_SERVED -> FINDING_SEAT
        assert state_machine.transition_to(StudentState.FINDING_SEAT, "test") is True
        assert state_machine.get_current_state() == StudentState.FINDING_SEAT

        # FINDING_SEAT -> DINING
        assert state_machine.transition_to(StudentState.DINING, "test") is True
        assert state_machine.get_current_state() == StudentState.DINING

        # DINING -> LEAVING
        assert state_machine.transition_to(StudentState.LEAVING, "test") is True
        assert state_machine.get_current_state() == StudentState.LEAVING

        # LEAVING -> LEFT
        assert state_machine.transition_to(StudentState.LEFT, "test") is True
        assert state_machine.get_current_state() == StudentState.LEFT

    def test_invalid_transitions(self):
        """测试无效状态转换"""
        state_machine = StudentStateMachine()

        # ARRIVED -> QUEUING (无效)
        assert state_machine.transition_to(StudentState.QUEUING, "test") is False
        assert state_machine.get_current_state() == StudentState.ARRIVED

        # 转移到当前状态 (无效，除非是初始化)
        assert state_machine.transition_to(StudentState.ARRIVED, "test") is False

        # 到达最终状态后不能再转移
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test")
        state_machine.transition_to(StudentState.LEAVING, "test")
        state_machine.transition_to(StudentState.LEFT, "test")

        assert state_machine.transition_to(StudentState.ARRIVED, "test") is False
        assert state_machine.get_current_state() == StudentState.LEFT

    def test_can_transition_to(self):
        """测试是否可以转换到目标状态"""
        state_machine = StudentStateMachine()

        # 当前状态是ARRIVED
        assert state_machine.can_transition_to(StudentState.SELECTING_CAFETERIA) is True
        assert state_machine.can_transition_to(StudentState.QUEUING) is False

        # 转换到SELECTING_CAFETERIA
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test")

        # 现在可以从SELECTING_CAFETERIA转换到QUEUING或LEAVING
        assert state_machine.can_transition_to(StudentState.QUEUING) is True
        assert state_machine.can_transition_to(StudentState.LEAVING) is True
        assert state_machine.can_transition_to(StudentState.ARRIVED) is False

    def test_transition_with_metadata(self):
        """测试带元数据的状态转换"""
        state_machine = StudentStateMachine()

        metadata = {"cafeteria_id": "cafeteria_1", "reason": "preference"}
        assert state_machine.transition_to(
            StudentState.SELECTING_CAFETERIA,
            "selection",
            metadata
        ) is True

        # 检查转换历史
        history = state_machine.get_transition_history()
        assert len(history) == 2  # 初始状态 + 一次转换

        transition = history[1]
        assert transition.from_state == StudentState.ARRIVED
        assert transition.to_state == StudentState.SELECTING_CAFETERIA
        assert transition.trigger == "selection"
        assert transition.metadata == metadata

    def test_state_duration(self):
        """测试状态持续时间"""
        state_machine = StudentStateMachine()

        # 初始状态的持续时间
        time.sleep(0.1)
        duration = state_machine.get_current_state_duration()
        assert duration >= 0.1

        # 转换到新状态
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test")
        time.sleep(0.1)

        # 新状态的持续时间
        duration = state_machine.get_current_state_duration()
        assert duration >= 0.1

        # 获取之前状态的总持续时间
        arrived_duration = state_machine.get_state_duration(StudentState.ARRIVED)
        assert arrived_duration >= 0.1

    def test_transition_history(self):
        """测试转换历史"""
        state_machine = StudentStateMachine()

        # 初始状态
        history = state_machine.get_transition_history()
        assert len(history) == 1
        assert history[0].from_state == StudentState.ARRIVED
        assert history[0].to_state == StudentState.ARRIVED
        assert history[0].trigger == "initialization"

        # 进行几次转换
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "select")
        state_machine.transition_to(StudentState.QUEUING, "queue")
        state_machine.transition_to(StudentState.LEAVING, "leave")

        history = state_machine.get_transition_history()
        assert len(history) == 4  # 初始 + 3次转换

        # 检查转换顺序
        assert history[1].to_state == StudentState.SELECTING_CAFETERIA
        assert history[2].to_state == StudentState.QUEUING
        assert history[3].to_state == StudentState.LEAVING

    def test_get_state_summary(self):
        """测试获取状态摘要"""
        state_machine = StudentStateMachine()

        # 初始状态摘要
        summary = state_machine.get_state_summary()
        assert summary["current_state"] == StudentState.ARRIVED.value
        assert summary["current_state_duration"] >= 0
        assert summary["total_transitions"] == 0
        assert summary["is_final_state"] is False
        assert StudentState.ARRIVED.value in summary["state_durations"]

        # 转换后
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test")
        time.sleep(0.05)

        summary = state_machine.get_state_summary()
        assert summary["current_state"] == StudentState.SELECTING_CAFETERIA.value
        assert summary["current_state_duration"] >= 0.05
        assert summary["total_transitions"] == 1
        assert summary["is_final_state"] is False

    def test_reset(self):
        """测试重置状态机"""
        state_machine = StudentStateMachine()

        # 进行一些转换
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "select")
        state_machine.transition_to(StudentState.QUEUING, "queue")
        time.sleep(0.1)

        # 重置
        state_machine.reset(StudentState.ARRIVED)

        # 检查状态
        assert state_machine.get_current_state() == StudentState.ARRIVED
        assert state_machine.get_current_state_duration() >= 0

        # 检查历史
        history = state_machine.get_transition_history()
        assert len(history) == 1
        assert history[0].trigger == "reset"

        # 检查状态持续时间
        for state in StudentState:
            if state == StudentState.ARRIVED:
                assert state_machine.get_state_duration(state) == 0.0
            else:
                assert state_machine.get_state_duration(state) == 0.0

    def test_is_final_state(self):
        """测试最终状态判断"""
        state_machine = StudentStateMachine()

        # 初始状态不是最终状态
        assert state_machine.get_state_summary()["is_final_state"] is False

        # 转换到LEFT状态
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "test")
        state_machine.transition_to(StudentState.LEAVING, "test")
        state_machine.transition_to(StudentState.LEFT, "test")

        assert state_machine.get_state_summary()["is_final_state"] is True

    def test_alternative_paths(self):
        """测试备选路径（如直接离开）"""
        state_machine = StudentStateMachine()

        # ARRIVED -> SELECTING_CAFETERIA -> LEAVING (不排队直接离开)
        assert state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "select") is True
        assert state_machine.transition_to(StudentState.LEAVING, "leave") is True
        assert state_machine.get_current_state() == StudentState.LEAVING

        # 重置测试其他路径
        state_machine.reset()

        # SELECTING_CAFETERIA -> QUEUING -> LEAVING (排队后放弃)
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "select")
        state_machine.transition_to(StudentState.QUEUING, "queue")
        assert state_machine.transition_to(StudentState.LEAVING, "abandon") is True

        # QUEUING -> BEING_SERVED -> FINDING_SEAT -> DINING -> LEAVING (完整流程)
        state_machine.reset()
        state_machine.transition_to(StudentState.SELECTING_CAFETERIA, "select")
        state_machine.transition_to(StudentState.QUEUING, "queue")
        state_machine.transition_to(StudentState.BEING_SERVED, "serve")
        state_machine.transition_to(StudentState.FINDING_SEAT, "find")
        state_machine.transition_to(StudentState.DINING, "dine")
        state_machine.transition_to(StudentState.LEAVING, "leave")
        assert state_machine.get_current_state() == StudentState.LEAVING