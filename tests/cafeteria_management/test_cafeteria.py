"""
食堂类单元测试
"""

import pytest
from cafeteria_management.cafeteria import Cafeteria, Seat, CafeteriaStats
from cafeteria_management.service_window import WindowStatus


class TestCafeteria:
    """食堂测试类"""

    def test_initialization(self):
        """测试初始化"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        assert cafeteria.cafeteria_id == "cafeteria_1"
        assert cafeteria.name == "第一食堂"
        assert cafeteria.total_seats == 50
        assert len(cafeteria.get_all_windows()) == 0
        assert cafeteria.get_available_seats_count() == 50

    def test_add_window(self):
        """测试添加窗口"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        # 添加窗口
        assert cafeteria.add_window("window_1", 1.0) is True
        assert cafeteria.add_window("window_2", 2.0) is True

        windows = cafeteria.get_all_windows()
        assert len(windows) == 2
        assert windows[0].window_id == "window_1"
        assert windows[1].window_id == "window_2"
        assert windows[0].service_rate == 1.0
        assert windows[1].service_rate == 2.0

        # 添加重复窗口应该失败
        assert cafeteria.add_window("window_1", 3.0) is False
        assert len(cafeteria.get_all_windows()) == 2

    def test_remove_window(self):
        """测试移除窗口"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        cafeteria.add_window("window_1", 1.0)
        cafeteria.add_window("window_2", 2.0)

        # 移除存在的窗口
        assert cafeteria.remove_window("window_1") is True
        assert len(cafeteria.get_all_windows()) == 1
        assert cafeteria.get_all_windows()[0].window_id == "window_2"

        # 移除不存在的窗口应该失败
        assert cafeteria.remove_window("window_3") is False
        assert len(cafeteria.get_all_windows()) == 1

    def test_get_window(self):
        """测试获取窗口"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        cafeteria.add_window("window_1", 1.0)
        cafeteria.add_window("window_2", 2.0)

        window = cafeteria.get_window("window_1")
        assert window is not None
        assert window.window_id == "window_1"
        assert window.service_rate == 1.0

        # 获取不存在的窗口
        assert cafeteria.get_window("window_3") is None

    def test_get_available_windows(self):
        """测试获取可用窗口"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        cafeteria.add_window("window_1", 1.0)
        cafeteria.add_window("window_2", 2.0)

        # 初始都应该是空闲状态
        available_windows = cafeteria.get_available_windows()
        assert len(available_windows) == 2

        # 关闭一个窗口
        window1 = cafeteria.get_window("window_1")
        window1.close_window()

        available_windows = cafeteria.get_available_windows()
        assert len(available_windows) == 1
        assert available_windows[0].window_id == "window_2"

    def test_find_best_window(self):
        """测试寻找最佳窗口"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 50)

        cafeteria.add_window("window_1", 1.0)
        cafeteria.add_window("window_2", 2.0)

        # 初始队列都为空，应该返回第一个窗口
        best_window = cafeteria.find_best_window()
        assert best_window is not None
        assert best_window.window_id == "window_1"

        # 向第一个窗口加入队列
        window1 = cafeteria.get_window("window_1")
        window1.enqueue_student("student_1")
        window1.enqueue_student("student_2")

        # 现在应该返回第二个窗口（队列更短）
        best_window = cafeteria.find_best_window()
        assert best_window.window_id == "window_2"

        # 关闭第二个窗口
        window2 = cafeteria.get_window("window_2")
        window2.close_window()

        # 现在应该返回第一个窗口（虽然队列长，但是唯一可用的）
        best_window = cafeteria.find_best_window()
        assert best_window.window_id == "window_1"

        # 关闭所有窗口
        window1.close_window()
        best_window = cafeteria.find_best_window()
        assert best_window is None

    def test_occupy_seat(self):
        """测试占用座位"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 3)  # 只有3个座位

        # 占用第一个座位
        seat_id1 = cafeteria.occupy_seat("student_1")
        assert seat_id1 is not None
        assert seat_id1.startswith("seat_cafeteria_1_")
        assert cafeteria.get_available_seats_count() == 2

        # 占用第二个座位
        seat_id2 = cafeteria.occupy_seat("student_2")
        assert seat_id2 is not None
        assert seat_id2 != seat_id1
        assert cafeteria.get_available_seats_count() == 1

        # 占用第三个座位
        seat_id3 = cafeteria.occupy_seat("student_3")
        assert seat_id3 is not None
        assert cafeteria.get_available_seats_count() == 0

        # 尝试占用第四个座位（应该失败）
        seat_id4 = cafeteria.occupy_seat("student_4")
        assert seat_id4 is None
        assert cafeteria.get_available_seats_count() == 0

        # 检查被占用的座位
        occupied_seats = cafeteria.get_occupied_seats()
        assert len(occupied_seats) == 3
        student_ids = {seat.occupied_by for seat in occupied_seats}
        assert student_ids == {"student_1", "student_2", "student_3"}

    def test_release_seat(self):
        """测试释放座位"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 3)

        # 占用一个座位
        seat_id = cafeteria.occupy_seat("student_1")
        assert seat_id is not None
        assert cafeteria.get_available_seats_count() == 2

        # 释放座位
        assert cafeteria.release_seat(seat_id) is True
        assert cafeteria.get_available_seats_count() == 3

        # 再次释放同一个座位应该失败
        assert cafeteria.release_seat(seat_id) is False

        # 释放不存在的座位应该失败
        assert cafeteria.release_seat("nonexistent_seat") is False

    def test_get_seat_info(self):
        """测试获取座位信息"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 3)

        # 占用一个座位
        seat_id = cafeteria.occupy_seat("student_1")

        seat_info = cafeteria.get_seat_info(seat_id)
        assert seat_info is not None
        assert seat_info["seat_id"] == seat_id
        assert seat_info["cafeteria_id"] == "cafeteria_1"
        assert seat_info["is_occupied"] is True
        assert seat_info["occupied_by"] == "student_1"
        assert seat_info["occupied_since"] is not None

        # 获取不存在的座位信息
        assert cafeteria.get_seat_info("nonexistent_seat") is None

    def test_get_cafeteria_stats(self):
        """测试获取食堂统计信息"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 10)

        # 初始统计
        stats = cafeteria.get_cafeteria_stats()
        assert stats.total_students_served == 0
        assert stats.total_seats_utilization == 0.0
        assert stats.peak_occupancy == 0
        assert stats.current_occupancy == 0

        # 占用一些座位
        cafeteria.occupy_seat("student_1")
        cafeteria.occupy_seat("student_2")
        cafeteria.occupy_seat("student_3")

        stats = cafeteria.get_cafeteria_stats()
        assert stats.current_occupancy == 3
        assert stats.peak_occupancy == 3
        assert stats.total_seats_utilization == 30.0  # 3/10 * 100

        # 释放一个座位
        seat_id = cafeteria.occupy_seat("student_4")  # 再占用一个
        cafeteria.release_seat(seat_id)

        stats = cafeteria.get_cafeteria_stats()
        assert stats.current_occupancy == 3
        assert stats.peak_occupancy == 4
        assert stats.total_students_served == 1

    def test_reset_stats(self):
        """测试重置统计信息"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 10)

        # 生成一些统计数据
        cafeteria.add_window("window_1", 1.0)
        cafeteria.occupy_seat("student_1")
        cafeteria.occupy_seat("student_2")

        stats_before = cafeteria.get_cafeteria_stats()
        assert stats_before.current_occupancy == 2
        assert stats_before.peak_occupancy == 2

        # 重置统计
        cafeteria.reset_stats()

        stats_after = cafeteria.get_cafeteria_stats()
        assert stats_after.current_occupancy == 2  # 当前占用状态保持不变
        assert stats_after.peak_occupancy == 2  # 峰值占用也保持不变
        assert stats_after.total_students_served == 0  # 总服务人数重置

    def test_get_cafeteria_info(self):
        """测试获取食堂完整信息"""
        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 10)

        # 添加窗口和占用座位
        cafeteria.add_window("window_1", 1.0)
        cafeteria.add_window("window_2", 2.0)
        cafeteria.occupy_seat("student_1")

        info = cafeteria.get_cafeteria_info()

        assert info["cafeteria_id"] == "cafeteria_1"
        assert info["name"] == "第一食堂"
        assert info["total_seats"] == 10
        assert info["available_seats"] == 9
        assert info["current_occupancy"] == 1
        assert info["peak_occupancy"] == 1
        assert info["seat_utilization"] == 10.0  # 1/10 * 100
        assert info["total_students_served"] == 0
        assert info["windows_count"] == 2
        assert len(info["windows"]) == 2
        assert len(info["seats"]) == 10

        # 验证窗口信息
        window_info = info["windows"][0]
        assert "window_id" in window_info
        assert "status" in window_info
        assert "queue_length" in window_info

        # 验证座位信息
        seat_info = info["seats"][0]
        assert "seat_id" in seat_info
        assert "is_occupied" in seat_info
        assert "occupied_by" in seat_info

    def test_thread_safety(self):
        """测试线程安全性"""
        import concurrent.futures

        cafeteria = Cafeteria("cafeteria_1", "第一食堂", 20)
        cafeteria.add_window("window_1", 1.0)

        student_counter = 0

        def worker():
            nonlocal student_counter
            import threading
            student_id = f"student_{threading.get_ident()}_{student_counter}"
            student_counter += 1

            # 占用座位
            seat_id = cafeteria.occupy_seat(student_id)
            if seat_id:
                # 加入队列
                window = cafeteria.get_window("window_1")
                if window:
                    window.enqueue_student(student_id)
                    # 模拟服务
                    if window.start_service():
                        import time
                        time.sleep(0.01)
                        window.complete_service()
                # 释放座位
                cafeteria.release_seat(seat_id)

        # 使用多个线程并发操作
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker) for _ in range(50)]
            concurrent.futures.wait(futures)

        # 检查最终状态
        stats = cafeteria.get_cafeteria_stats()
        assert stats.total_students_served <= 50
        assert cafeteria.get_available_seats_count() == 20  # 所有座位应该都被释放了