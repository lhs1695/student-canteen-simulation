"""
学生类单元测试
"""

import time
import pytest
from student_behavior.student import Student, StudentPreferences, StudentBehavior
from student_behavior.student_state import StudentState


class TestStudent:
    """学生测试类"""

    def test_initialization(self):
        """测试初始化"""
        # 使用默认参数
        student = Student()
        assert student.student_id.startswith("student_")
        assert student.get_current_state() == StudentState.ARRIVED
        assert student.arrival_time > 0
        assert student.departure_time is None

        # 指定ID和偏好
        preferences = StudentPreferences(
            preferred_cafeteria_id="cafeteria_1",
            max_wait_time=300.0,
            dining_duration_range=(600.0, 1200.0),
            patience_level=0.7,
            walking_speed=1.2
        )
        student = Student("custom_student_id", preferences)

        assert student.student_id == "custom_student_id"
        assert student.preferences.preferred_cafeteria_id == "cafeteria_1"
        assert student.preferences.max_wait_time == 300.0
        assert student.preferences.patience_level == 0.7
        assert student.preferences.walking_speed == 1.2

    def test_select_cafeteria(self):
        """测试选择食堂"""
        student = Student()

        # 从ARRIVED状态可以选择食堂（select_cafeteria方法内部处理状态转换）
        assert student.select_cafeteria("cafeteria_1") is True
        assert student.get_current_state() == StudentState.SELECTING_CAFETERIA

        # 检查行为记录
        behavior = student.get_behavior_info()
        assert behavior.selected_cafeteria_id == "cafeteria_1"

        # 测试重复选择
        student = Student()
        student.select_cafeteria("cafeteria_1")
        # 已经选择食堂后，不能再次选择（状态不再是ARRIVED）
        # 实际上select_cafeteria会失败，因为不能从SELECTING_CAFETERIA转换到SELECTING_CAFETERIA
        assert student.select_cafeteria("cafeteria_2") is False
        assert student.get_behavior_info().selected_cafeteria_id == "cafeteria_1"

    def test_start_queuing(self):
        """测试开始排队"""
        student = Student()

        # 选择食堂
        student.select_cafeteria("cafeteria_1")

        # 开始排队
        assert student.start_queuing("window_1") is True
        assert student.get_current_state() == StudentState.QUEUING

        # 检查行为记录
        behavior = student.get_behavior_info()
        assert behavior.selected_window_id == "window_1"
        assert behavior.queue_start_time is not None
        assert behavior.queue_start_time > 0

        # 错误的状态转换
        student = Student()
        assert student.start_queuing("window_1") is False  # 从ARRIVED不能直接排队

    def test_start_service(self):
        """测试开始服务"""
        student = Student()

        # 完整流程：选择食堂 -> 排队 -> 开始服务
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        assert student.start_service() is True
        assert student.get_current_state() == StudentState.BEING_SERVED

        # 检查行为记录
        behavior = student.get_behavior_info()
        assert behavior.service_start_time is not None
        assert behavior.service_start_time > 0

        # 错误的状态转换
        student = Student()
        assert student.start_service() is False  # 从ARRIVED不能直接开始服务

    def test_finish_service(self):
        """测试完成服务"""
        student = Student()

        # 完整流程
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        student.start_service()
        time.sleep(0.1)

        assert student.finish_service() is True
        assert student.get_current_state() == StudentState.FINDING_SEAT

    def test_find_seat(self):
        """测试找到座位"""
        student = Student()

        # 完整流程
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        student.start_service()
        student.finish_service()

        assert student.find_seat("seat_1") is True
        assert student.get_current_state() == StudentState.DINING

        # 检查行为记录
        behavior = student.get_behavior_info()
        assert behavior.occupied_seat_id == "seat_1"
        assert behavior.dining_start_time is not None
        assert behavior.dining_start_time > 0

    def test_start_leaving(self):
        """测试开始离开"""
        student = Student()

        # 从不同状态开始离开
        test_cases = [
            (StudentState.ARRIVED, False),  # 不能直接从ARRIVED离开
            (StudentState.SELECTING_CAFETERIA, True),
            (StudentState.QUEUING, True),
            (StudentState.BEING_SERVED, True),
            (StudentState.FINDING_SEAT, True),
            (StudentState.DINING, True),
        ]

        for target_state, expected_result in test_cases:
            student = Student()
            if target_state != StudentState.ARRIVED:
                # 转换到目标状态
                student.select_cafeteria("cafeteria_1")
                if target_state == StudentState.QUEUING:
                    student.start_queuing("window_1")
                elif target_state == StudentState.BEING_SERVED:
                    student.start_queuing("window_1")
                    student.start_service()
                elif target_state == StudentState.FINDING_SEAT:
                    student.start_queuing("window_1")
                    student.start_service()
                    student.finish_service()
                elif target_state == StudentState.DINING:
                    student.start_queuing("window_1")
                    student.start_service()
                    student.finish_service()
                    student.find_seat("seat_1")

            result = student.start_leaving()
            assert result == expected_result, f"Failed for {target_state}: expected {expected_result}, got {result}"

            if expected_result:
                assert student.get_current_state() == StudentState.LEAVING

    def test_complete_leaving(self):
        """测试完成离开"""
        student = Student()

        # 完整流程到最后
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        student.start_service()
        student.finish_service()
        student.find_seat("seat_1")
        student.start_leaving()

        assert student.complete_leaving() is True
        assert student.get_current_state() == StudentState.LEFT
        assert student.departure_time is not None
        assert student.departure_time >= student.arrival_time

        # 错误的状态转换
        student = Student()
        assert student.complete_leaving() is False  # 不能从ARRIVED直接完成离开

    def test_abandon_queue(self):
        """测试放弃排队"""
        student = Student()

        # 在排队状态放弃
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        assert student.abandon_queue() is True
        assert student.get_current_state() == StudentState.LEAVING

        # 在服务状态放弃
        student = Student()
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        student.start_service()

        assert student.abandon_queue() is True
        assert student.get_current_state() == StudentState.LEAVING

        # 错误的状态（不在排队或服务中）
        student = Student()
        assert student.abandon_queue() is False

        student.select_cafeteria("cafeteria_1")
        assert student.abandon_queue() is False  # 在选择食堂状态

    def test_get_behavior_info(self):
        """测试获取行为信息"""
        student = Student("test_student")

        # 初始行为信息
        behavior = student.get_behavior_info()
        assert isinstance(behavior, StudentBehavior)
        assert behavior.selected_cafeteria_id is None
        assert behavior.selected_window_id is None
        assert behavior.occupied_seat_id is None
        assert behavior.queue_start_time is None
        assert behavior.service_start_time is None
        assert behavior.dining_start_time is None

        # 执行一些操作后
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        behavior = student.get_behavior_info()
        assert behavior.selected_cafeteria_id == "cafeteria_1"
        assert behavior.selected_window_id == "window_1"
        assert behavior.queue_start_time is not None

    def test_get_state_summary(self):
        """测试获取状态摘要"""
        student = Student("test_student")

        summary = student.get_state_summary()

        assert summary["student_id"] == "test_student"
        assert summary["arrival_time"] > 0
        assert summary["departure_time"] is None
        assert summary["total_time_in_system"] >= 0
        assert summary["current_state"] == StudentState.ARRIVED.value
        assert summary["is_final_state"] is False

        # 检查偏好
        assert "preferences" in summary
        prefs = summary["preferences"]
        assert "preferred_cafeteria_id" in prefs
        assert "max_wait_time" in prefs
        assert "dining_duration_range" in prefs
        assert "patience_level" in prefs
        assert "walking_speed" in prefs

        # 检查行为
        assert "behavior" in summary
        behavior = summary["behavior"]
        assert "selected_cafeteria_id" in behavior
        assert "selected_window_id" in behavior
        assert "occupied_seat_id" in behavior

    def test_is_waiting_too_long(self):
        """测试是否等待时间过长"""
        # 创建耐心水平低的学生
        preferences = StudentPreferences(
            max_wait_time=10.0,  # 最大等待10秒
            patience_level=0.1   # 耐心水平很低
        )
        student = Student("impatient_student", preferences)

        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        # 刚开始等待不应该太长
        assert student.is_waiting_too_long() is False

        # 创建耐心水平高的学生
        preferences = StudentPreferences(
            max_wait_time=10.0,  # 最大等待10秒
            patience_level=1.0   # 耐心水平很高
        )
        student = Student("patient_student", preferences)

        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        # 即使等待一会儿，耐心高的学生也不会觉得太长
        time.sleep(0.1)
        assert student.is_waiting_too_long() is False

        # 不在等待状态
        student = Student()
        assert student.is_waiting_too_long() is False

    def test_get_estimated_dining_duration(self):
        """测试获取预计就餐时长"""
        preferences = StudentPreferences(
            dining_duration_range=(5.0, 10.0)  # 5-10秒
        )
        student = Student("test_student", preferences)

        duration = student.get_estimated_dining_duration()
        assert 5.0 <= duration <= 10.0

        # 多次调用可能得到不同的值（随机）
        durations = {student.get_estimated_dining_duration() for _ in range(10)}
        assert len(durations) > 1  # 很可能得到不同的值

    def test_should_abandon(self):
        """测试是否应该放弃"""
        # 创建耐心水平很低的学生
        preferences = StudentPreferences(
            max_wait_time=0.01,  # 最大等待0.01秒
            patience_level=0.1   # 耐心水平很低
        )
        student = Student("very_impatient_student", preferences)

        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")

        # 等待一小段时间后应该放弃
        time.sleep(0.02)
        assert student.should_abandon() is True

        # 不在等待状态
        student = Student()
        assert student.should_abandon() is False

    def test_reset(self):
        """测试重置学生状态"""
        preferences = StudentPreferences(
            preferred_cafeteria_id="original_cafeteria",
            max_wait_time=300.0
        )
        student = Student("test_student", preferences)

        # 执行一些操作
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        time.sleep(0.1)

        # 记录之前的状态
        old_arrival_time = student.arrival_time
        old_behavior = student.get_behavior_info()

        # 重置
        new_preferences = StudentPreferences(
            preferred_cafeteria_id="new_cafeteria",
            max_wait_time=600.0
        )
        student.reset(new_preferences)

        # 检查状态重置
        assert student.get_current_state() == StudentState.ARRIVED
        assert student.arrival_time > old_arrival_time  # 新的到达时间
        assert student.departure_time is None

        # 检查偏好更新
        assert student.preferences.preferred_cafeteria_id == "new_cafeteria"
        assert student.preferences.max_wait_time == 600.0

        # 检查行为重置
        new_behavior = student.get_behavior_info()
        assert new_behavior.selected_cafeteria_id is None
        assert new_behavior.selected_window_id is None
        assert new_behavior.queue_start_time is None

        # 不指定新偏好，保持原有偏好
        student.reset()
        assert student.preferences.preferred_cafeteria_id == "new_cafeteria"  # 保持不变

    def test_get_transition_history(self):
        """测试获取转换历史"""
        student = Student("test_student")

        # 初始状态
        history = student.get_transition_history()
        assert len(history) == 1

        # 执行一些转换
        student.select_cafeteria("cafeteria_1")
        student.start_queuing("window_1")
        student.start_service()

        history = student.get_transition_history()
        assert len(history) == 4  # 初始 + 3次转换

        # 检查转换顺序
        assert history[1].to_state == StudentState.SELECTING_CAFETERIA
        assert history[2].to_state == StudentState.QUEUING
        assert history[3].to_state == StudentState.BEING_SERVED

    def test_thread_safety(self):
        """测试线程安全性"""
        import concurrent.futures
        import threading

        students = []
        results = []

        def worker(student_id):
            """工作线程函数"""
            try:
                preferences = StudentPreferences(
                    preferred_cafeteria_id=f"cafeteria_{threading.get_ident()}",
                    max_wait_time=100.0,
                    patience_level=0.5
                )
                student = Student(student_id, preferences)

                # 执行一系列操作
                student.select_cafeteria("cafeteria_1")
                student.start_queuing("window_1")
                student.start_service()
                time.sleep(0.01)
                student.finish_service()
                student.find_seat("seat_1")
                student.start_leaving()
                student.complete_leaving()

                # 获取状态摘要
                summary = student.get_state_summary()
                results.append((student_id, summary["current_state"]))
                students.append(student)
            except Exception as e:
                print(f"Error in worker {student_id}: {e}")
                raise

        # 使用多个线程并发创建和操作学生
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, f"student_{i}") for i in range(20)]
            concurrent.futures.wait(futures)

        # 检查结果
        assert len(results) == 20
        for student_id, final_state in results:
            assert final_state == StudentState.LEFT.value, f"Student {student_id} final state is {final_state}"

        # 检查所有学生都到达最终状态
        for student in students:
            assert student.get_current_state() == StudentState.LEFT
            assert student.departure_time is not None