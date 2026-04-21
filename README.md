# 多食堂多窗口仿真系统

## 项目概述

这是一个学生食堂仿真实验系统，采用分层模块化设计。系统包含6个模块：仿真控制、事件调度、食堂管理、学生行为、数据接口、前端展示。

## 项目结构

```bash
multi_cafeteria_simulation/
├── cafeteria_management/     # 食堂管理模块
│   ├── __init__.py          # 模块导出定义
│   ├── cafeteria.py         # 食堂类实现
│   ├── manager.py           # 食堂管理器
│   └── service_window.py    # 服务窗口类
├── student_behavior/        # 学生行为模块
│   ├── __init__.py          # 模块导出定义
│   ├── student.py           # 学生类实现
│   └── student_state.py     # 学生状态机
├── tests/                   # 单元测试
│   ├── cafeteria_management/  # 食堂管理测试
│   │   ├── test_cafeteria.py
│   │   ├── test_manager.py
│   │   └── test_service_window.py
│   └── student_behavior/     # 学生行为测试
│       ├── test_student.py
│       └── test_student_state.py
├── demo.py                  # 系统功能演示脚本
├── setup.py                 # 项目安装配置
├── requirements.txt         # Python依赖包列表
├── API_INTERFACE.md         # 详细接口文档
└── README.md                # 项目说明文档
```

## 模块详细说明

### 1. 食堂管理模块 (`cafeteria_management/`)

**职责**：管理多个食堂及其内部资源状态，提供线程安全的资源分配和状态查询接口。

#### 核心组件

1. **CafeteriaManager** (`manager.py`) - 食堂管理器
   - 创建和删除食堂
   - 统一管理多个食堂资源
   - 提供系统级统计信息
   - 线程安全的全局资源管理

2. **Cafeteria** (`cafeteria.py`) - 食堂类
   - 管理单个食堂的窗口和座位资源
   - 实现最佳窗口选择算法
   - 座位占用和释放管理
   - 食堂级统计信息收集

3. **ServiceWindow** (`service_window.py`) - 服务窗口类
   - 管理窗口队列（FIFO）
   - 服务开始和完成控制
   - 等待时间预估计算
   - 窗口状态管理（空闲、服务中、关闭）

#### 文件功能说明

- `__init__.py`: 模块导出定义，统一管理公共接口，导出类包括ServiceWindow, WindowStatus, ServiceStats, Cafeteria, Seat, CafeteriaStats, CafeteriaManager
- `cafeteria.py`: 包含Cafeteria类，管理食堂窗口和座位资源，提供窗口管理（添加、移除、查询）、座位管理（占用、释放）、最佳窗口选择、统计信息收集等功能
- `manager.py`: 包含CafeteriaManager类，负责食堂的创建和删除、跨食堂的资源分配（窗口分配、座位占用）、系统级状态查询和统计、最佳食堂选择算法
- `service_window.py`: 包含ServiceWindow类，管理窗口队列、服务控制、等待时间计算，支持基于服务速率的等待时间预估和队列容量限制

#### 关键特性

- 支持多食堂、多窗口并行服务
- 智能窗口分配（队列最短优先）
- 座位资源管理（占用/释放）
- 实时状态查询和统计
- 完整的线程安全设计

### 2. 学生行为模块 (`student_behavior/`)

**职责**：管理单个学生的生命周期状态，模拟学生在食堂系统中的完整行为流程。

#### 核心组件

1. **Student** (`student.py`) - 学生类
   - 管理学生的完整生命周期
   - 实现食堂选择、排队、服务、就餐、离开等行为
   - 基于偏好的行为决策（耐心水平、等待时间等）
   - 线程安全的并发操作

2. **StudentStateMachine** (`student_state.py`) - 学生状态机
   - 定义8种学生状态（到达、选择食堂、排队中、服务中、寻找座位、就餐中、离开中、已离开）
   - 管理状态转换逻辑和有效性验证
   - 记录完整的状态转换历史
   - 状态持续时间跟踪

#### 文件功能说明

- `__init__.py`: 模块导出定义，导出类包括StudentState, StudentStateMachine, StateTransition, Student, StudentPreferences, StudentBehavior
- `student_state.py`: 包含StudentState枚举（定义8种学生状态）、StateTransition记录数据模型、StudentStateMachine类（处理状态转换逻辑、历史记录、持续时间跟踪）
- `student.py`: 包含Student类，实现学生生命周期管理，包括食堂选择、排队、服务、就餐、离开等完整流程；还包括StudentPreferences（学生偏好配置）和StudentBehavior（学生行为记录）类

#### 行为特性

- 完整的状态机设计，支持多种行为路径
- 个性化学生偏好设置（食堂偏好、耐心水平、就餐时长等）
- 智能决策机制（是否放弃排队、等待时间评估）
- 详细的行为记录和历史追踪

### 3. 测试模块 (`tests/`)

#### 测试结构

- `tests/cafeteria_management/` - 食堂管理模块测试
  - `test_cafeteria.py` (13个测试) - 食堂类功能测试
  - `test_manager.py` (11个测试) - 食堂管理器测试
  - `test_service_window.py` (12个测试) - 服务窗口测试

- `tests/student_behavior/` - 学生行为模块测试
  - `test_student.py` (20个测试) - 学生类功能测试
  - `test_student_state.py` (11个测试) - 学生状态机测试

#### 测试特性

- **全面覆盖**：67个测试用例，覆盖所有核心功能
- **线程安全测试**：每个模块都包含多线程并发测试
- **边界条件测试**：队列容量、座位上限、超时处理等
- **状态转换测试**：合法和非法状态转换验证

## 其他文件说明

### `demo.py`

- **功能**：系统功能演示脚本
- **演示内容**：
  - 食堂管理模块演示：创建食堂、添加窗口、占用座位、查询信息
  - 学生行为模块演示：创建学生、完整生命周期流程、行为决策
  - 集成演示：学生与食堂系统的交互
- **使用方式**：`python demo.py`

### `setup.py`

- **功能**：项目安装配置
- **配置项**：项目名称、版本、描述、作者信息、依赖包、Python版本要求
- **使用方式**：`pip install -e .`（开发模式安装）

### `requirements.txt`

- **功能**：Python依赖包列表
- **包含**：`pytest>=7.0.0`, `pytest-cov>=4.0.0`
- **使用方式**：`pip install -r requirements.txt`

### `API_INTERFACE.md`

- **功能**：详细的接口文档
- **内容**：
  - 食堂管理模块所有公共接口说明
  - 学生行为模块所有公共接口说明
  - 使用注意事项和错误处理建议
- **用途**：开发人员参考文档，便于模块集成和扩展

## 安装和使用

### 环境要求

- Python 3.12
- pip包管理工具

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd student_canteen_simulation

# 安装依赖
pip install -r requirements.txt

# 可选：以开发模式安装项目
pip install -e .
```

### 运行测试

```bash
# 推荐方式（避免路径问题）
python -m pytest tests/ -v

# 或使用pytest直接运行（需确保当前目录在Python路径中）
pytest tests/ -v
```

### 运行演示

```bash
python demo.py
```
