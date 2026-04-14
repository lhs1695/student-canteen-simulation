"""
食堂管理器单元测试
"""

import pytest
from cafeteria_management.manager import CafeteriaManager


class TestCafeteriaManager:
    """食堂管理器测试类"""

    def test_initialization(self):
        """测试初始化"""
        manager = CafeteriaManager()

        assert len(manager.get_all_cafeterias()) == 0
        assert manager.get_all_cafeterias_info() == []

    def test_create_cafeteria(self):
        """测试创建食堂"""
        manager = CafeteriaManager()

        # 创建食堂
        assert manager.create_cafeteria("cafeteria_1", "第一食堂", 50) is True
        assert manager.create_cafeteria("cafeteria_2", "第二食堂", 30) is True

        cafeterias = manager.get_all_cafeterias()
        assert len(cafeterias) == 2
        assert cafeterias[0].cafeteria_id == "cafeteria_1"
        assert cafeterias[1].cafeteria_id == "cafeteria_2"

        # 创建重复食堂应该失败
        assert manager.create_cafeteria("cafeteria_1", "重复食堂", 10) is False
        assert len(manager.get_all_cafeterias()) == 2

    def test_remove_cafeteria(self):
        """测试移除食堂"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)
        manager.create_cafeteria("cafeteria_2", "第二食堂", 30)

        # 移除存在的食堂
        assert manager.remove_cafeteria("cafeteria_1") is True
        assert len(manager.get_all_cafeterias()) == 1
        assert manager.get_all_cafeterias()[0].cafeteria_id == "cafeteria_2"

        # 移除不存在的食堂应该失败
        assert manager.remove_cafeteria("cafeteria_3") is False
        assert len(manager.get_all_cafeterias()) == 1

    def test_get_cafeteria(self):
        """测试获取食堂"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)

        cafeteria = manager.get_cafeteria("cafeteria_1")
        assert cafeteria is not None
        assert cafeteria.cafeteria_id == "cafeteria_1"
        assert cafeteria.name == "第一食堂"
        assert cafeteria.total_seats == 50

        # 获取不存在的食堂
        assert manager.get_cafeteria("nonexistent_cafeteria") is None

    def test_get_cafeteria_info(self):
        """测试获取食堂信息"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)
        manager.add_window_to_cafeteria("cafeteria_1", "window_1", 1.0)

        info = manager.get_cafeteria_info("cafeteria_1")
        assert info is not None
        assert info["cafeteria_id"] == "cafeteria_1"
        assert info["name"] == "第一食堂"
        assert info["total_seats"] == 50
        assert info["windows_count"] == 1

        # 获取不存在的食堂信息
        assert manager.get_cafeteria_info("nonexistent_cafeteria") is None

    def test_get_all_cafeterias_info(self):
        """测试获取所有食堂信息"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)
        manager.create_cafeteria("cafeteria_2", "第二食堂", 30)

        all_info = manager.get_all_cafeterias_info()
        assert len(all_info) == 2
        assert all_info[0]["cafeteria_id"] == "cafeteria_1"
        assert all_info[1]["cafeteria_id"] == "cafeteria_2"

    def test_find_best_cafeteria(self):
        """测试寻找最佳食堂"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 5)  # 5个座位
        manager.create_cafeteria("cafeteria_2", "第二食堂", 3)  # 3个座位

        # 初始都有空位，应该返回第一个
        best_cafeteria = manager.find_best_cafeteria()
        assert best_cafeteria == "cafeteria_1"

        # 占用第一食堂的所有座位
        for i in range(5):
            manager.occupy_seat("cafeteria_1", f"student_{i}")

        # 现在应该返回第二食堂
        best_cafeteria = manager.find_best_cafeteria()
        assert best_cafeteria == "cafeteria_2"

        # 占用第二食堂的所有座位
        for i in range(3):
            manager.occupy_seat("cafeteria_2", f"student_{i+5}")

        # 现在应该返回None（没有空位）
        best_cafeteria = manager.find_best_cafeteria()
        assert best_cafeteria is None

        # 测试偏好食堂
        # 释放第二食堂的一个座位（先获取一个已占用的座位ID）
        cafeteria2 = manager.get_cafeteria("cafeteria_2")
        occupied_seats = cafeteria2.get_occupied_seats() # type: ignore
        assert len(occupied_seats) == 3
        seat_id = occupied_seats[0].seat_id

        manager.release_seat("cafeteria_2", seat_id)

        # 有偏好时应该返回偏好食堂（如果有空位）
        best_cafeteria = manager.find_best_cafeteria("cafeteria_1")
        # 第一食堂已满，但第二食堂有空位，所以返回第二食堂
        assert best_cafeteria == "cafeteria_2"

        best_cafeteria = manager.find_best_cafeteria("cafeteria_2")
        assert best_cafeteria == "cafeteria_2"  # 第二食堂有空位

    def test_allocate_window(self):
        """测试分配窗口"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)
        manager.add_window_to_cafeteria("cafeteria_1", "window_1", 1.0)
        manager.add_window_to_cafeteria("cafeteria_1", "window_2", 2.0)

        # 分配窗口
        window_id = manager.allocate_window("cafeteria_1")
        assert window_id == "window_1"  # 初始队列都为空，返回第一个

        # 向第一个窗口加入队列
        cafeteria = manager.get_cafeteria("cafeteria_1")
        window1 = cafeteria.get_window("window_1") # type: ignore
        window1.enqueue_student("student_1") # type: ignore

        # 现在应该返回第二个窗口
        window_id = manager.allocate_window("cafeteria_1")
        assert window_id == "window_2"

        # 不存在的食堂
        window_id = manager.allocate_window("nonexistent_cafeteria")
        assert window_id is None

    def test_occupy_seat(self):
        """测试占用座位"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 5)

        # 占用座位
        seat_id = manager.occupy_seat("cafeteria_1", "student_1")
        assert seat_id is not None
        assert seat_id.startswith("seat_cafeteria_1_")

        # 检查座位确实被占用
        cafeteria = manager.get_cafeteria("cafeteria_1")
        assert cafeteria.get_available_seats_count() == 4 # type: ignore

        # 不存在的食堂
        seat_id = manager.occupy_seat("nonexistent_cafeteria", "student_2")
        assert seat_id is None

    def test_release_seat(self):
        """测试释放座位"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 5)

        # 占用然后释放座位
        seat_id = manager.occupy_seat("cafeteria_1", "student_1")
        assert seat_id is not None

        assert manager.release_seat("cafeteria_1", seat_id) is True
        assert manager.get_cafeteria("cafeteria_1").get_available_seats_count() == 5 # type: ignore

        # 再次释放应该失败
        assert manager.release_seat("cafeteria_1", seat_id) is False

        # 不存在的食堂或座位
        assert manager.release_seat("nonexistent_cafeteria", seat_id) is False
        assert manager.release_seat("cafeteria_1", "nonexistent_seat") is False

    def test_add_window_to_cafeteria(self):
        """测试为食堂添加窗口"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)

        # 添加窗口
        assert manager.add_window_to_cafeteria("cafeteria_1", "window_1", 1.0) is True
        assert manager.add_window_to_cafeteria("cafeteria_1", "window_2", 2.0) is True

        cafeteria = manager.get_cafeteria("cafeteria_1")
        assert len(cafeteria.get_all_windows()) == 2 # type: ignore

        # 添加重复窗口应该失败
        assert manager.add_window_to_cafeteria("cafeteria_1", "window_1", 3.0) is False

        # 不存在的食堂
        assert manager.add_window_to_cafeteria("nonexistent_cafeteria", "window_3", 1.0) is False

    def test_get_system_stats(self):
        """测试获取系统整体统计信息"""
        manager = CafeteriaManager()

        # 空系统
        stats = manager.get_system_stats()
        assert stats["total_cafeterias"] == 0
        assert stats["total_windows"] == 0
        assert stats["total_seats"] == 0
        assert stats["seat_utilization_rate"] == 0

        # 创建两个食堂
        manager.create_cafeteria("cafeteria_1", "第一食堂", 10)
        manager.create_cafeteria("cafeteria_2", "第二食堂", 20)

        # 添加窗口
        manager.add_window_to_cafeteria("cafeteria_1", "window_1", 1.0)
        manager.add_window_to_cafeteria("cafeteria_2", "window_2", 2.0)
        manager.add_window_to_cafeteria("cafeteria_2", "window_3", 3.0)

        # 占用一些座位
        manager.occupy_seat("cafeteria_1", "student_1")
        manager.occupy_seat("cafeteria_2", "student_2")
        manager.occupy_seat("cafeteria_2", "student_3")

        stats = manager.get_system_stats()
        assert stats["total_cafeterias"] == 2
        assert stats["total_windows"] == 3
        assert stats["total_seats"] == 30  # 10 + 20
        assert stats["total_available_seats"] == 27  # 30 - 3
        assert stats["total_occupied_seats"] == 3
        assert 9.9 <= stats["seat_utilization_rate"] <= 10.1  # 3/30 * 100 ≈ 10

    def test_clear_all(self):
        """测试清空所有食堂"""
        manager = CafeteriaManager()

        manager.create_cafeteria("cafeteria_1", "第一食堂", 50)
        manager.create_cafeteria("cafeteria_2", "第二食堂", 30)
        manager.add_window_to_cafeteria("cafeteria_1", "window_1", 1.0)

        assert len(manager.get_all_cafeterias()) == 2

        manager.clear_all()

        assert len(manager.get_all_cafeterias()) == 0
        assert manager.get_all_cafeterias_info() == []

    def test_thread_safety(self):
        """测试线程安全性"""
        import concurrent.futures
        import time

        manager = CafeteriaManager()

        # 创建一些食堂
        for i in range(3):
            manager.create_cafeteria(f"cafeteria_{i}", f"食堂_{i}", 10)
            manager.add_window_to_cafeteria(f"cafeteria_{i}", f"window_{i}_1", 1.0)
            manager.add_window_to_cafeteria(f"cafeteria_{i}", f"window_{i}_2", 2.0)

        operation_count = 0

        def worker():
            nonlocal operation_count
            import threading
            thread_id = threading.get_ident()

            # 执行各种操作
            for i in range(20):
                cafeteria_id = f"cafeteria_{i % 3}"
                student_id = f"student_{thread_id}_{i}"

                # 占用座位
                seat_id = manager.occupy_seat(cafeteria_id, student_id)
                if seat_id:
                    # 分配窗口
                    window_id = manager.allocate_window(cafeteria_id)
                    if window_id:
                        # 获取食堂信息
                        info = manager.get_cafeteria_info(cafeteria_id)
                        assert info is not None

                    # 释放座位
                    manager.release_seat(cafeteria_id, seat_id)

                operation_count += 1

        # 使用多个线程并发操作
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker) for _ in range(10)]
            concurrent.futures.wait(futures)

        # 检查最终状态
        stats = manager.get_system_stats()
        assert stats["total_cafeterias"] == 3
        assert stats["total_windows"] == 6
        assert stats["total_seats"] == 30
        # 所有座位应该都被释放了
        assert stats["total_available_seats"] == 30