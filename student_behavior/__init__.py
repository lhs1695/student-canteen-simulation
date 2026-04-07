"""
学生行为模块
管理单个学生的生命周期状态
"""

from .student_state import StudentState, StudentStateMachine, StateTransition
from .student import Student, StudentPreferences, StudentBehavior

__version__ = "1.0.0"
__all__ = [
    "StudentState",
    "StudentStateMachine",
    "StateTransition",
    "Student",
    "StudentPreferences",
    "StudentBehavior"
]