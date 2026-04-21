# 食堂管理模块和学生行为模块接口说明

本文档详细描述了食堂管理模块和学生行为模块的公共接口，供其他模块开发人员参考。

## 食堂管理模块接口

### 1. CafeteriaManager（食堂管理器）

#### 创建和管理食堂

- `create_cafeteria(cafeteria_id: str, name: str, total_seats: int) -> bool`
  - 功能：创建新食堂
  - 参数：食堂唯一标识符、名称、总座位数
  - 返回：是否成功创建

- `remove_cafeteria(cafeteria_id: str) -> bool`
  - 功能：移除食堂
  - 参数：食堂ID
  - 返回：是否成功移除

- `get_cafeteria(cafeteria_id: str) -> Optional[Cafeteria]`
  - 功能：获取指定食堂对象
  - 参数：食堂ID
  - 返回：食堂对象或None

#### 食堂状态查询

- `get_cafeteria_info(cafeteria_id: str) -> Optional[Dict[str, Any]]`
  - 功能：获取食堂详细信息
  - 参数：食堂ID
  - 返回：包含食堂信息的字典或None

- `get_all_cafeterias_info() -> List[Dict[str, Any]]`
  - 功能：获取所有食堂信息
  - 返回：所有食堂信息的列表

- `find_best_cafeteria(preference: Optional[str] = None) -> Optional[str]`
  - 功能：寻找最佳食堂（通常是最少队列或首选食堂）
  - 参数：偏好食堂ID（可选）
  - 返回：最佳食堂ID或None

#### 窗口管理

- `add_window_to_cafeteria(cafeteria_id: str, window_id: str, service_rate: float = 1.0) -> bool`
  - 功能：为食堂添加窗口
  - 参数：食堂ID、窗口ID、服务速率
  - 返回：是否成功添加

- `allocate_window(cafeteria_id: str) -> Optional[str]`
  - 功能：在指定食堂分配最佳窗口
  - 参数：食堂ID
  - 返回：窗口ID或None

#### 座位管理

- `occupy_seat(cafeteria_id: str, student_id: str) -> Optional[str]`
  - 功能：在指定食堂占用座位
  - 参数：食堂ID、学生ID
  - 返回：座位ID或None

- `release_seat(cafeteria_id: str, seat_id: str) -> bool`
  - 功能：在指定食堂释放座位
  - 参数：食堂ID、座位ID
  - 返回：是否成功释放

#### 系统统计

- `get_system_stats() -> Dict[str, Any]`
  - 功能：获取系统整体统计信息
  - 返回：包含统计信息的字典
  - 包含：食堂总数、窗口总数、座位总数、可用座位、占用座位、座位利用率等

### 2. Cafeteria（食堂类）

#### 窗口操作

- `get_window(window_id: str) -> Optional[ServiceWindow]`
  - 功能：获取指定窗口对象
  - 返回：窗口对象或None

- `find_best_window() -> Optional[ServiceWindow]`
  - 功能：寻找最佳窗口（队列最短的窗口）
  - 返回：窗口对象或None

#### 座位操作

- `get_available_seats_count() -> int`
  - 功能：获取可用座位数
  - 返回：可用座位数

- `get_occupied_seats() -> List[Seat]`
  - 功能：获取被占用的座位列表
  - 返回：被占用座位的列表

#### 食堂信息

- `get_cafeteria_info() -> Dict[str, Any]`
  - 功能：获取食堂完整信息
  - 返回：包含食堂所有信息的字典

### 3. ServiceWindow（服务窗口类）

#### 队列操作

- `enqueue_student(student_id: str) -> bool`
  - 功能：学生加入队列
  - 参数：学生ID
  - 返回：是否成功加入队列

- `dequeue_student() -> Optional[str]`
  - 功能：从队列中取出下一个学生
  - 返回：学生ID或None

- `get_queue_length() -> int`
  - 功能：获取当前队列长度
  - 返回：队列长度

#### 服务操作

- `start_service() -> bool`
  - 功能：开始为下一个学生服务
  - 返回：是否成功开始服务

- `complete_service() -> Optional[str]`
  - 功能：完成当前服务
  - 返回：被服务的学生ID或None

- `get_status() -> WindowStatus`
  - 功能：获取窗口状态（IDLE, SERVING, CLOSED）
  - 返回：窗口状态枚举

- `get_estimated_wait_time() -> float`
  - 功能：获取预计等待时间
  - 返回：预计等待时间（秒）

## 学生行为模块接口

### 1. Student（学生类）

#### 状态转换方法

- `select_cafeteria(cafeteria_id: str) -> bool`
  - 功能：选择食堂
  - 参数：食堂ID
  - 返回：是否成功选择

- `start_queuing(window_id: str) -> bool`
  - 功能：开始排队
  - 参数：窗口ID
  - 返回：是否成功开始排队

- `start_service() -> bool`
  - 功能：开始服务
  - 返回：是否成功开始服务

- `finish_service() -> bool`
  - 功能：完成服务，开始寻找座位
  - 返回：是否成功完成服务

- `find_seat(seat_id: str) -> bool`
  - 功能：找到座位，开始就餐
  - 参数：座位ID
  - 返回：是否成功找到座位

- `start_leaving() -> bool`
  - 功能：开始离开
  - 返回：是否成功开始离开

- `complete_leaving() -> bool`
  - 功能：完成离开
  - 返回：是否成功离开系统

- `abandon_queue() -> bool`
  - 功能：放弃排队
  - 返回：是否成功放弃

#### 状态查询方法

- `get_current_state() -> StudentState`
  - 功能：获取当前状态
  - 返回：当前学生状态枚举

- `get_state_summary() -> Dict[str, Any]`
  - 功能：获取状态摘要
  - 返回：包含学生完整状态信息的字典
  - 包含：学生ID、到达时间、离开时间、总系统时间、当前状态、状态持续时间、偏好设置等

- `get_transition_history() -> List[StateTransition]`
  - 功能：获取状态转换历史
  - 返回：状态转换历史列表

#### 行为决策方法

- `is_waiting_too_long() -> bool`
  - 功能：检查是否等待时间过长
  - 返回：是否等待时间过长

- `should_abandon() -> bool`
  - 功能：判断是否应该放弃（基于耐心水平和等待时间）
  - 返回：是否应该放弃

- `get_estimated_dining_duration() -> float`
  - 功能：获取预计就餐时长
  - 返回：预计就餐时长（秒）

### 2. StudentPreferences（学生偏好类）

- 构造函数参数：
  - `preferred_cafeteria_id: Optional[str]` - 偏好食堂ID
  - `max_wait_time: float` - 最大等待时间（秒）
  - `dining_duration_range: tuple[float, float]` - 就餐时长范围（秒）
  - `patience_level: float` - 耐心水平（0.0-1.0）
  - `walking_speed: float` - 行走速度（米/秒）

### 3. StudentState（学生状态枚举）

- `ARRIVED` - 到达系统
- `SELECTING_CAFETERIA` - 选择食堂
- `QUEUING` - 排队中
- `BEING_SERVED` - 服务中
- `FINDING_SEAT` - 寻找座位
- `DINING` - 就餐中
- `LEAVING` - 离开中
- `LEFT` - 已离开系统

## 使用注意事项

1. 所有模块都是线程安全的，可以在多线程环境下使用。
2. 在调用占用座位、加入队列等操作前，应先检查是否有可用资源。
3. 在调用释放资源的方法前，应确保资源已被占用。
4. 学生状态转换需遵循预定义的有效转换路径，否则会失败。
5. 请妥善处理接口返回的Optional类型值，避免未预期的None值导致错误。

## 错误处理建议

1. 在调用任何接口时，应检查返回值以确认操作是否成功。
2. 对于返回Optional类型的接口，请务必检查返回值是否为None。
3. 在集成时，建议使用try-catch机制捕获可能的异常。
