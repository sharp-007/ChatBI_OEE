# ChatBI OEE — 智能制造 OEE 分析平台

> **传统仪表盘 + AI 对话分析，智能对话式的OEE可视化分析平台**

制造业的 OEE（Overall Equipment Effectiveness，设备综合效率）分析长期依赖固定报表和预设图表，业务人员难以灵活下钻和自由探索数据。ChatBI OEE 将 **传统 BI 仪表盘** 与 **基于自然语言的智能对话分析** 融合为一体：

- **仪表盘模式** — 提供 OEE 概览、趋势分析、设备排名、停机分析、六大损失等经典可视化面板，支持产线筛选与时间范围切换，满足日常监控与管理汇报需求
- **对话模式** — 用户以中文自然语言提问（如"哪台设备的停机时间最长？"），系统通过 NL2SQL 自动生成 SQL、执行查询、解读结果并推荐最佳图表，实现零门槛的数据探索

在 NL2SQL 工程层面，本项目聚焦于 **Schema 注入方案的实践**，采用 **元数据表集中管理（Level 3）** 策略，将表结构、字段语义、业务规则统一存储在 `schema_metadata` 表中，运行时动态构建 Prompt，兼顾可维护性与 NL2SQL 准确率。

## 演示视频

[![Video Demo](https://img.youtube.com/vi/uN0ACWdIo_w/maxresdefault.jpg)](https://www.youtube.com/watch?v=uN0ACWdIo_w)

## 功能特性

### 对话式智能分析

- **自然语言查询** — 输入中文问题，AI 自动生成 SQL 并执行，无需了解数据库结构
- **多轮对话记忆** — 支持最近 5 轮上下文追问，如"上个月呢？""按车间拆分"
- **智能图表推荐** — LLM 根据数据特征自动选择最佳图表类型，支持颜色分类图例
- **结果解读** — AI 对查询结果进行业务解读，给出数据洞察而非仅展示数字

### OEE 可视化仪表盘

- **四大指标概览** — OEE、可用率、性能率、质量率仪表盘，一目了然
- **趋势分析** — 支持按天/周/月聚合，世界级 OEE 85% 达标线标注
- **产线筛选** — 仪表盘全局产线过滤，按需聚焦分析
- **设备排名 & 车间对比** — 横向对比设备效率与车间表现
- **停机分析** — 停机原因分布饼图 + 设备停机时长排名
- **六大损失** — 可用性/性能/质量三维度损失量化

### 工程能力

- **SQL 安全校验** — 白名单 + 黑名单双重防护，仅允许 SELECT 查询
- **Schema 元数据管理** — 表结构语义集中维护，支持动态更新无需重启

## 技术栈

| 层级     | 技术            | 说明                                        |
| -------- | --------------- | ------------------------------------------- |
| LLM      | 通义千问 (Qwen) | DashScope API，NL2SQL + 结果解读 + 图表推荐 |
| 后端     | FastAPI         | REST API 服务，CORS 跨域支持                |
| 前端     | Streamlit       | 多页面应用，对话 + 仪表盘双模式             |
| 数据库   | MySQL 8.0+      | 生产数据存储 + OEE 计算视图                 |
| 数据访问 | SQLAlchemy      | 连接池管理 + 原生 SQL 执行                  |
| 可视化   | Plotly          | 6 种图表类型自动渲染                        |

## 项目结构

```
ChatBI_OEE/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                 # 环境变量配置
│   │   ├── models/
│   │   │   └── database.py           # ORM 模型 (含 SchemaMetadata)
│   │   ├── services/
│   │   │   ├── llm_service.py        # 通义千问 API 封装
│   │   │   ├── nl2sql.py             # NL2SQL 核心引擎
│   │   │   ├── db_service.py         # SQL 执行 + Schema 动态构建
│   │   │   └── oee_calculator.py     # OEE 预定义查询
│   │   ├── api/
│   │   │   └── routes.py             # 7 个 REST API 端点
│   │   └── prompts/
│   │       └── nl2sql_prompt.py      # 三套 Prompt 模板
│   └── requirements.txt
├── frontend/                         # 前端应用
│   ├── app.py                        # Streamlit 主页
│   ├── pages/
│   │   ├── 1_💬_对话查询.py           # 对话查询页面
│   │   └── 2_📈_OEE仪表盘.py         # OEE 仪表盘页面
│   ├── components/
│   │   ├── charts.py                 # Plotly 图表组件 (6种)
│   │   └── sidebar.py                # 侧边栏组件
│   └── requirements.txt
├── database/
│   ├── schema.sql                    # 建表 + 元数据表 + OEE 视图
│   ├── seed_data.sql                 # 3 个月模拟生产数据
│   └── schema_metadata_seed.sql      # Schema 元数据种子数据
├── .env.example                      # 环境变量模板
└── README.md
```

## 系统架构

### 整体架构

```mermaid
graph TB
    U(["用户"])

    subgraph Frontend["前端 Streamlit"]
        Chat["对话查询\n自然语言提问 / 多轮对话"]
        Dashboard["OEE 仪表盘\n概览 / 趋势 / 排名 / 停机 / 损失"]
        Charts["图表引擎\nPlotly 6 种图表自动渲染"]
    end

    subgraph Backend["后端 FastAPI"]
        API["REST API\n7 个端点 / CORS"]
        NL2SQL["NL2SQL 引擎\nPrompt 构建 / SQL 清洗 / 安全校验"]
        SchemaBuilder["Schema 构建器\n元数据动态加载 / TTL 缓存"]
        OEECalc["OEE 计算器\n预定义查询 / 产线筛选"]
    end

    subgraph External["外部服务"]
        LLM["通义千问 Qwen\nDashScope API"]
    end

    subgraph DB["MySQL 数据库"]
        BizData[("业务数据\n设备 / 产品 / 生产记录\n停机记录 / OEE 视图")]
        Meta[("schema_metadata\n表字段语义 / 业务规则\n示例值 / 排序权重")]
    end

    U --> Chat
    U --> Dashboard
    Chat --> API
    Dashboard --> API
    API --> NL2SQL
    API --> OEECalc
    NL2SQL --> SchemaBuilder
    SchemaBuilder -->|动态读取| Meta
    NL2SQL -->|1 生成SQL| LLM
    NL2SQL -->|2 执行SQL| BizData
    NL2SQL -->|3 解读结果| LLM
    NL2SQL -->|4 推荐图表| LLM
    OEECalc --> BizData
    API --> Charts
    Charts --> U

    style Frontend fill:#e8f4fd,stroke:#2196f3,stroke-width:2px
    style Backend fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style DB fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style External fill:#fce4ec,stroke:#e91e63,stroke-width:2px
```

### NL2SQL 处理流水线

```mermaid
graph LR
    Q["用户提问"] --> CTX["上下文拼接\n最近5轮对话"]
    CTX --> SCHEMA["Schema注入\n从metadata表动态构建"]
    SCHEMA --> PROMPT["Prompt组装\nSystem+Schema+History"]
    PROMPT --> GEN["LLM生成SQL"]
    GEN --> CLEAN["SQL清洗\nUnicode修正/注释移除"]
    CLEAN --> SAFE{"安全校验\n白名单+黑名单"}
    SAFE -->|通过| EXEC["执行SQL"]
    SAFE -->|拒绝| ERR["拒绝执行"]
    EXEC --> INTERP["LLM解读结果"]
    EXEC --> CHART["LLM推荐图表\n类型/字段/颜色"]
    INTERP --> RENDER["渲染展示"]
    CHART --> RENDER

    style Q fill:#e3f2fd,stroke:#1565c0
    style SAFE fill:#fff9c4,stroke:#f9a825
    style ERR fill:#ffebee,stroke:#c62828
    style RENDER fill:#e8f5e9,stroke:#2e7d32
```

### 数据库设计

#### ER 关系

```mermaid
graph LR
    E["equipment\n设备主数据"]
    P["product\n产品主数据"]
    PR["production_record\n生产记录"]
    DR["downtime_record\n停机记录"]
    OD[/"oee_daily\nOEE日汇总视图"/]
    SM["schema_metadata\n元数据管理"]

    E -->|1:N| PR
    E -->|1:N| DR
    P -->|1:N| PR
    PR -.->|JOIN汇总| OD

    style E fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style P fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style PR fill:#fff3e0,stroke:#ff9800
    style DR fill:#fff3e0,stroke:#ff9800
    style OD fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style SM fill:#fce4ec,stroke:#e91e63
```

#### 表清单

| 表名                  | 类型   | 用途                                                  |
| --------------------- | ------ | ----------------------------------------------------- |
| `equipment`         | 主数据 | 设备编号、名称、类型、车间、产线、理论节拍            |
| `product`           | 主数据 | 产品编号、名称、类别                                  |
| `production_record` | 事务   | 生产记录（实际运行时长、产出、合格数、不良数）        |
| `downtime_record`   | 事务   | 停机事件（类型、分类、原因、时长）                    |
| `oee_daily`         | 视图   | 自动 JOIN 设备+产品，实时计算可用率/性能率/质量率/OEE |
| `schema_metadata`   | 元数据 | NL2SQL Schema 注入的语义标注管理                      |

### Schema 注入方案

本项目实践了 NL2SQL Schema 注入从简单到复杂的演进路径。当前采用 **Level 3（元数据表标注）**，后续可平滑升级到 Level 4（RAG 检索）以支持更大规模的数据库。

```mermaid
graph LR
    L1["<b>Level 1</b><br/>硬编码文本<br/><small>10张表以下</small>"]
    L2["<b>Level 2</b><br/>自动提取DDL<br/><small>快速原型</small>"]
    L3["<b>Level 3</b><br/>元数据表标注<br/><small>✅ 本项目当前</small>"]
    L4["<b>Level 4</b><br/>动态Schema检索<br/><small>50+张表</small>"]
    L5["<b>Level 5</b><br/>知识图谱/语义层<br/><small>超大型系统</small>"]

    L1 --> L2 --> L3 --> L4 --> L5

    style L3 fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style L1 fill:#f5f5f5,stroke:#9e9e9e
    style L2 fill:#f5f5f5,stroke:#9e9e9e
    style L4 fill:#e3f2fd,stroke:#1565c0,stroke-dasharray:5 5
    style L5 fill:#e3f2fd,stroke:#1565c0,stroke-dasharray:5 5
```

#### Schema 注入架构

本项目的核心设计是 **元数据表驱动的 Schema 注入**，取代传统的硬编码方式。

```mermaid
graph TB
    META[("schema_metadata 表\n表/字段/语义/业务规则")] -->|"SQL查询 WHERE is_important=TRUE"| BUILD

    subgraph SchemaEngine["Schema 构建引擎"]
        BUILD["_build_schema_from_metadata\n按表分组 - 拼接字段描述 - 附加规则"]
        CACHE["TTL 缓存 5min\n避免高频查询"]
        FALLBACK["降级方案\n硬编码Schema兜底"]
        BUILD --> CACHE
        BUILD -.->|元数据表异常| FALLBACK
    end

    CACHE -->|Schema文本| PROMPT["NL2SQL System Prompt\n数据库结构注入"]
    PROMPT --> LLM["通义千问 Qwen\n生成SQL - 执行 - 解读"]

    style META fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style SchemaEngine fill:#fff8e1,stroke:#ffc107,stroke-width:2px
    style PROMPT fill:#e3f2fd,stroke:#1976d2
    style LLM fill:#fce4ec,stroke:#e91e63
```

#### 元数据表结构

| 字段              | 说明                                    |
| ----------------- | --------------------------------------- |
| `table_name`    | 表/视图名，`_global` 表示全局业务规则 |
| `column_name`   | 字段名，NULL 表示表级描述               |
| `column_type`   | 字段类型 (如 `INT`、`VARCHAR(50)`)  |
| `description`   | 中文语义描述                            |
| `sample_values` | 示例值/枚举值                           |
| `business_rule` | 业务规则和查询提示                      |
| `is_important`  | 是否注入 Prompt（控制 Schema 精简度）   |
| `sort_order`    | 展示排序权重                            |

#### 日常维护

```sql
-- 新增字段
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sort_order)
VALUES ('equipment', 'new_field', 'VARCHAR(50)', '新字段描述', 10);

-- 修改描述
UPDATE schema_metadata SET description='更新后的描述' WHERE table_name='equipment' AND column_name='workshop';

-- 隐藏字段（不注入 Prompt）
UPDATE schema_metadata SET is_important=FALSE WHERE table_name='downtime_record' AND column_name='id';
```

修改后等待缓存过期（5 分钟）或重启服务即可生效。

## 快速开始

### 1. 环境准备

- Python 3.10+（推荐 Conda 管理）
- MySQL 8.0+
- 通义千问 API Key（[申请地址](https://dashscope.console.aliyun.com/)）

### 2. 创建虚拟环境

```bash
conda create -n chatbi python=3.10 -y
conda activate chatbi
```

### 3. 安装依赖

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置：

```env
DASHSCOPE_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=chatbi_oee
```

### 5. 初始化数据库

进入 MySQL 交互终端，依次执行以下脚本：

```bash
mysql -u root -p
```

```sql
-- 建表（含 schema_metadata 元数据表 + oee_daily 视图）
SOURCE database/schema.sql;

-- 导入模拟生产数据（10 台设备、8 种产品、2026年1-3月工作日数据）
SOURCE database/seed_data.sql;

-- 导入 Schema 元数据（表/字段的中文描述、示例值、业务规则）
SOURCE database/schema_metadata_seed.sql;
```

> **注意**：`seed_data.sql` 使用了存储过程和 `DELIMITER`，必须在 MySQL 交互终端中执行，不能通过管道或重定向方式导入。

### 6. 启动后端

```bash
python -m backend.app.main
```

后端 API 运行在 `http://localhost:8000`，接口文档访问 `http://localhost:8000/docs`。

### 7. 启动前端（新终端窗口）

```bash
streamlit run frontend/app.py
```

前端运行在 `http://localhost:8501`。

### 8. API 接口

| 接口                              | 方法 | 说明                         |
| --------------------------------- | ---- | ---------------------------- |
| `/api/v1/chat`                  | POST | 自然语言查询（支持多轮对话） |
| `/api/v1/oee/overview`          | GET  | OEE 概览（四大指标均值）     |
| `/api/v1/oee/trend`             | GET  | OEE 趋势（按天/周/月聚合）   |
| `/api/v1/oee/equipment-ranking` | GET  | 设备 OEE 排名                |
| `/api/v1/oee/workshop-summary`  | GET  | 车间维度对比                 |
| `/api/v1/oee/downtime-analysis` | GET  | 停机分类分析                 |
| `/api/v1/oee/loss-analysis`     | GET  | 六大损失分析                 |

### 9. 自然语言查询示例

```
"本月OEE最高的设备是哪台？"
"一车间3月份的OEE趋势如何？"
"哪台设备的停机时间最长？"
"各车间的质量率对比情况"
"2月份非计划停机的主要原因是什么？"
"注塑机的可用率和性能率表现"
"生产计划完成率最高的产品是哪个？"
```

### 10. OEE 计算公式

```
OEE = 可用率 × 性能率 × 质量率

可用率(Availability) = 实际运行时间 / 计划生产时间
性能率(Performance)  = (理论节拍 × 总产出) / (实际运行时间 × 60)
质量率(Quality)      = 合格数量 / 总产出数量
```

| 指标   | 世界级水平 | 良好   | 需改善 |
| ------ | ---------- | ------ | ------ |
| OEE    | >= 85%     | 70-85% | < 70%  |
| 可用率 | >= 90%     | —     | —     |
| 性能率 | >= 95%     | —     | —     |
| 质量率 | >= 99%     | —     | —     |

## 作者

**Joyce Pan (潘姣)**

- GitHub：[@sharp-007](https://github.com/sharp-007)
- Email：panjiao007@126.com
- LinkedIn：[joyce-pan-549596138](https://www.linkedin.com/in/joyce-pan-549596138)

如有任何问题或建议，欢迎通过 Issue 交流。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。
