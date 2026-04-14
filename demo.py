"""
多食堂多窗口仿真系统演示

展示食堂管理模块和学生行为模块的基本功能
"""

import time
from cafeteria_management import CafeteriaManager
from student_behavior import Student, StudentPreferences


def demo_cafeteria_management():
    """演示食堂管理模块"""
    print("=" * 60)
    print("食堂管理模块演示")
    print("=" * 60)

    # 创建食堂管理器
    manager = CafeteriaManager()

    # 创建两个食堂
    manager.create_cafeteria("cafeteria_1", "第一食堂", 10)
    manager.create_cafeteria("cafeteria_2", "第二食堂", 8)

    # 为食堂添加窗口
    manager.add_window_to_cafeteria("cafeteria_1", "window_1_1", 1.0)
    manager.add_window_to_cafeteria("cafeteria_1", "window_1_2", 2.0)
    manager.add_window_to_cafeteria("cafeteria_2", "window_2_1", 1.5)

    print(f"创建了 {len(manager.get_all_cafeterias())} 个食堂")

    # 占用座位
    seat_id_1 = manager.occupy_seat("cafeteria_1", "student_1")
    seat_id_2 = manager.occupy_seat("cafeteria_2", "student_2")

    if seat_id_1:
        print(f"学生1在食堂1占用座位: {seat_id_1}")
    else:
        print("学生1未能在食堂1占用到座位")
        
    if seat_id_2:
        print(f"学生2在食堂2占用座位: {seat_id_2}")
    else:
        print("学生2未能在食堂2占用到座位")

    # 获取食堂信息
    cafeteria_info = manager.get_cafeteria_info("cafeteria_1")
    if cafeteria_info:
        print(f"\n食堂1信息:")
        print(f"  名称: {cafeteria_info['name']}")
        print(f"  总座位: {cafeteria_info['total_seats']}")
        print(f"  可用座位: {cafeteria_info['available_seats']}")
        print(f"  当前占用: {cafeteria_info['current_occupancy']}")
        print(f"  窗口数量: {cafeteria_info['windows_count']}")
    else:
        print(f"\n无法获取食堂1信息: 食堂不存在")

    # 寻找最佳食堂
    best_cafeteria = manager.find_best_cafeteria()
    print(f"\n最佳食堂: {best_cafeteria}")

    # 分配窗口
    window_id = manager.allocate_window("cafeteria_1")
    print(f"在食堂1分配的最佳窗口: {window_id}")

    # 系统统计
    stats = manager.get_system_stats()
    print(f"\n系统统计:")
    print(f"  食堂总数: {stats['total_cafeterias']}")
    print(f"  窗口总数: {stats['total_windows']}")
    print(f"  座位总数: {stats['total_seats']}")
    print(f"  可用座位: {stats['total_available_seats']}")
    print(f"  占用座位: {stats['total_occupied_seats']}")
    print(f"  座位利用率: {stats['seat_utilization_rate']:.1f}%")

    # 释放座位
    if seat_id_1:
        manager.release_seat("cafeteria_1", seat_id_1)
    if seat_id_2:
        manager.release_seat("cafeteria_2", seat_id_2)

    print(f"\n释放座位后，食堂1可用座位: {manager.get_cafeteria('cafeteria_1').get_available_seats_count()}") # type: ignore


def demo_student_behavior():
    """演示学生行为模块"""
    print("\n" + "=" * 60)
    print("学生行为模块演示")
    print("=" * 60)

    # 创建学生偏好
    preferences = StudentPreferences(
        preferred_cafeteria_id="cafeteria_1",
        max_wait_time=300.0,
        dining_duration_range=(600.0, 1200.0),
        patience_level=0.8,
        walking_speed=1.2
    )

    # 创建学生
    student = Student("student_001", preferences)

    print(f"创建学生: {student.student_id}")
    print(f"初始状态: {student.get_current_state().value}")
    print(f"到达时间: {time.ctime(student.arrival_time)}")

    # 学生选择食堂
    student.select_cafeteria("cafeteria_1")
    print(f"\n选择食堂后状态: {student.get_current_state().value}")

    # 学生开始排队
    student.start_queuing("window_1_1")
    print(f"开始排队后状态: {student.get_current_state().value}")

    # 学生开始服务
    student.start_service()
    print(f"开始服务后状态: {student.get_current_state().value}")

    # 完成服务
    time.sleep(0.1)  # 模拟服务时间
    student.finish_service()
    print(f"完成服务后状态: {student.get_current_state().value}")

    # 找到座位
    student.find_seat("seat_1")
    print(f"找到座位后状态: {student.get_current_state().value}")

    # 开始离开
    student.start_leaving()
    print(f"开始离开后状态: {student.get_current_state().value}")

    # 完成离开
    student.complete_leaving()
    print(f"完成离开后状态: {student.get_current_state().value}")
    print(f"离开时间: {time.ctime(student.departure_time)}")

    # 获取状态摘要
    summary = student.get_state_summary()
    print(f"\n学生状态摘要:")
    print(f"  总时间: {summary['total_time_in_system']:.1f}秒")
    print(f"  状态转换次数: {summary['total_transitions']}")
    print(f"  是否最终状态: {summary['is_final_state']}")

    # 显示状态持续时间
    print(f"\n各状态持续时间:")
    for state, duration in summary['state_durations'].items():
        if duration > 0:
            print(f"  {state}: {duration:.2f}秒")


def demo_integration():
    """演示两个模块的独立工作（不互相依赖）"""
    print("\n" + "=" * 60)
    print("模块独立性演示")
    print("=" * 60)

    print("1. 食堂管理模块独立运行:")
    manager = CafeteriaManager()
    manager.create_cafeteria("demo_cafeteria", "演示食堂", 5)
    manager.add_window_to_cafeteria("demo_cafeteria", "demo_window", 1.0)

    print("   - 创建食堂和窗口成功")
    print("   - 食堂管理模块不依赖学生行为模块")

    print("\n2. 学生行为模块独立运行:")
    student = Student("demo_student")
    student.select_cafeteria("some_cafeteria")
    student.start_queuing("some_window")

    print("   - 学生状态转换成功")
    print("   - 学生行为模块不依赖食堂管理模块")

    print("\n3. 模块完全独立，通过外部系统协调:")
    print("   - 仿真控制模块负责协调两个模块")
    print("   - 事件调度模块负责时间推进")
    print("   - 数据接口模块提供通信")
    print("   - 前端展示模块提供可视化")


def main():
    """主函数"""
    print("多食堂多窗口仿真系统 - 模块演示")
    print("=" * 60)

    demo_cafeteria_management()
    demo_student_behavior()
    demo_integration()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()