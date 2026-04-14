"""
服务窗口单元测试
"""

import time
import pytest
from cafeteria_management.service_window import ServiceWindow, WindowStatus, ServiceStats


class TestServiceWindow:
    """服务窗口测试类"""

    def test_initialization(self):
        """测试初始化"""
        window = ServiceWindow("window_1", "cafeteria_1", 2.0)

        assert window.window_id == "window_1"
        assert window.cafeteria_id == "cafeteria_1"
        assert window.service_rate == 2.0
        assert window.get_status() == WindowStatus.IDLE
        assert window.get_current_student() is None
        assert window.get_queue_length() == 0

    def test_enqueue_student(self):
        """测试学生加入队列"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 成功加入队列
        assert window.enqueue_student("student_1") is True
        assert window.get_queue_length() == 1

        # 再次加入不同学生
        assert window.enqueue_student("student_2") is True
        assert window.get_queue_length() == 2

        # 加入相同学生（允许，因为实际中可能重复加入）
        assert window.enqueue_student("student_1") is True
        assert window.get_queue_length() == 3

    def test_enqueue_max_capacity(self):
        """测试队列容量上限"""
        window = ServiceWindow("window_1", "cafeteria_1")
        window.max_queue_capacity = 3  # 设置较小的容量进行测试

        # 加入3个学生应该都成功
        for i in range(3):
            assert window.enqueue_student(f"student_{i}") is True

        # 第4个应该失败
        assert window.enqueue_student("student_4") is False
        assert window.get_queue_length() == 3

    def test_dequeue_student(self):
        """测试从队列中取出学生"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 空队列
        assert window.dequeue_student() is None

        # 加入几个学生
        window.enqueue_student("student_1")
        window.enqueue_student("student_2")
        window.enqueue_student("student_3")

        # 取出应该是先进先出
        assert window.dequeue_student() == "student_1"
        assert window.get_queue_length() == 2
        assert window.dequeue_student() == "student_2"
        assert window.get_queue_length() == 1
        assert window.dequeue_student() == "student_3"
        assert window.get_queue_length() == 0
        assert window.dequeue_student() is None

    def test_start_service(self):
        """测试开始服务"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 空队列时开始服务应该失败
        assert window.start_service() is False
        assert window.get_status() == WindowStatus.IDLE
        assert window.get_current_student() is None

        # 加入学生到队列
        window.enqueue_student("student_1")

        # 从空闲状态开始服务
        assert window.start_service() is True
        assert window.get_status() == WindowStatus.SERVING
        assert window.get_current_student() == "student_1"

        # 服务中时不能开始新服务
        assert window.start_service() is False
        assert window.get_current_student() == "student_1"

    def test_complete_service(self):
        """测试完成服务"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 没有服务时完成服务
        assert window.complete_service() is None
        assert window.get_status() == WindowStatus.IDLE

        # 开始服务然后完成
        window.enqueue_student("student_1")
        window.start_service()
        time.sleep(0.1)  # 等待一小段时间
        student_id = window.complete_service()

        assert student_id == "student_1"
        assert window.get_status() == WindowStatus.IDLE
        assert window.get_current_student() is None

        # 检查统计信息
        stats = window.get_stats()
        assert stats.total_served == 1
        assert stats.total_service_time > 0

    def test_close_and_open_window(self):
        """测试关闭和打开窗口"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 关闭窗口
        assert window.close_window() is True
        assert window.get_status() == WindowStatus.CLOSED

        # 再次关闭应该失败
        assert window.close_window() is False

        # 打开窗口
        assert window.open_window() is True
        assert window.get_status() == WindowStatus.IDLE

        # 再次打开应该失败
        assert window.open_window() is False

    def test_get_estimated_wait_time(self):
        """测试获取预计等待时间"""
        window = ServiceWindow("window_1", "cafeteria_1", service_rate=1.0)  # 1人/秒

        # 空队列
        wait_time = window.get_estimated_wait_time()
        assert wait_time == 0.0

        # 加入队列
        window.enqueue_student("student_1")
        wait_time = window.get_estimated_wait_time()
        assert wait_time == 1.0  # 1人 * 1秒/人

        window.enqueue_student("student_2")
        wait_time = window.get_estimated_wait_time()
        assert wait_time == 2.0  # 2人 * 1秒/人

        # 服务中的情况
        # 先清空队列，重新设置测试场景
        window = ServiceWindow("window_1", "cafeteria_1", service_rate=1.0)
        window.enqueue_student("student_1")  # 第一个在队列中
        window.enqueue_student("student_2")  # 第二个在队列中
        window.start_service()  # 开始服务第一个学生
        time.sleep(0.3)
        wait_time = window.get_estimated_wait_time()
        # 应该是当前服务剩余时间(0.7) + 队列等待时间(1.0) = 1.7左右
        assert 1.6 <= wait_time <= 1.8

    def test_get_stats(self):
        """测试获取统计信息"""
        window = ServiceWindow("window_1", "cafeteria_1", service_rate=1.0)

        # 初始统计
        stats = window.get_stats()
        assert stats.total_served == 0
        assert stats.total_service_time == 0.0
        assert stats.avg_service_time == 0.0
        assert stats.max_queue_length == 0
        assert stats.current_queue_length == 0

        # 加入队列
        window.enqueue_student("student_1")
        window.enqueue_student("student_2")

        stats = window.get_stats()
        assert stats.current_queue_length == 2
        assert stats.max_queue_length == 2

        # 服务一个学生
        window.start_service()  # 从队列中取出student_1开始服务
        time.sleep(0.2)
        window.complete_service()

        stats = window.get_stats()
        assert stats.total_served == 1
        assert stats.total_service_time > 0
        assert stats.avg_service_time > 0
        assert stats.current_queue_length == 1  # 还有一个在队列中（student_2）

    def test_reset_stats(self):
        """测试重置统计信息"""
        window = ServiceWindow("window_1", "cafeteria_1")

        # 生成一些统计数据（加入队列但不服务）
        window.enqueue_student("student_1")
        window.enqueue_student("student_2")

        # 获取重置前的统计
        stats_before = window.get_stats()
        assert stats_before.current_queue_length == 2
        assert stats_before.max_queue_length == 2

        # 重置统计
        window.reset_stats()

        stats_after = window.get_stats()
        assert stats_after.total_served == 0
        assert stats_after.total_service_time == 0.0
        assert stats_after.max_queue_length == 0  # max_queue_length 被重置
        assert stats_after.current_queue_length == 2  # current_queue_length 应该不变

        # 队列状态应该保持不变
        assert window.get_queue_length() == 2

    def test_get_window_info(self):
        """测试获取窗口完整信息"""
        window = ServiceWindow("window_1", "cafeteria_1", service_rate=2.0)

        info = window.get_window_info()

        assert info["window_id"] == "window_1"
        assert info["cafeteria_id"] == "cafeteria_1"
        assert info["status"] == "idle"
        assert info["current_student"] is None
        assert info["queue_length"] == 0
        assert info["service_rate"] == 2.0
        assert info["estimated_wait_time"] == 0.0
        assert "stats" in info

        # 验证stats结构
        stats = info["stats"]
        assert "total_served" in stats
        assert "total_service_time" in stats
        assert "avg_service_time" in stats
        assert "max_queue_length" in stats
        assert "current_queue_length" in stats

    def test_thread_safety(self):
        """测试线程安全性"""
        import concurrent.futures

        window = ServiceWindow("window_1", "cafeteria_1")

        def worker(student_id):
            window.enqueue_student(student_id)
            time.sleep(0.01)
            if window.get_queue_length() > 0:
                dequeued = window.dequeue_student()
                if dequeued:
                    window.start_service()
                    time.sleep(0.01)
                    window.complete_service()

        # 使用多个线程并发操作
        student_ids = [f"student_{i}" for i in range(100)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, sid) for sid in student_ids]
            concurrent.futures.wait(futures)

        # 检查最终状态
        stats = window.get_stats()
        assert stats.total_served <= 100  # 可能有些被丢弃
        assert window.get_queue_length() == 0
        assert window.get_status() == WindowStatus.IDLE