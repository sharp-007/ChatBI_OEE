# ChatBI OEE - 智能对话式OEE可视化分析平台

基于自然语言查询的 **OEE（设备综合效率）** 可视化报表系统。用户通过对话式交互提出数据分析问题，系统自动将自然语言转换为SQL查询，并以图表形式展示分析结果。

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端框架 | Streamlit |
| 数据库 | MySQL |
| LLM | 通义千问 (Qwen) via DashScope API |
| ORM | SQLAlchemy |
| 图表库 | Plotly |

## 功能特性

- **自然语言查询**：输入中文问题，AI自动生成SQL并执行查询
- **智能图表推荐**：根据查询结果自动选择最佳图表类型
- **OEE仪表盘**：实时展示OEE概览、趋势、设备排名、停机分析
- **六大损失分析**：可用性损失、性能损失、质量损失可视化
- **SQL安全校验**：仅允许SELECT查询，防止数据篡改

## 项目结构

```
ChatBI_OEE/
├── backend/                     # 后端服务
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置管理
│   │   ├── models/database.py   # ORM模型
│   │   ├── services/
│   │   │   ├── llm_service.py   # 通义千问调用
│   │   │   ├── nl2sql.py        # NL2SQL核心
│   │   │   ├── oee_calculator.py # OEE计算
│   │   │   └── db_service.py    # 数据库服务
│   │   ├── api/routes.py        # API路由
│   │   └── prompts/             # Prompt模板
│   └── requirements.txt
├── frontend/                    # 前端应用
│   ├── app.py                   # Streamlit主页
│   ├── pages/
│   │   ├── 1_💬_对话查询.py      # 对话查询页
│   │   └── 2_📈_OEE仪表盘.py    # 仪表盘页
│   ├── components/
│   │   ├── charts.py            # 图表组件
│   │   └── sidebar.py           # 侧边栏
│   └── requirements.txt
├── database/
│   ├── schema.sql               # 建表脚本
│   └── seed_data.sql            # 演示数据
├── .env.example                 # 环境变量模板
└── README.md
```

## 快速开始

### 1. 环境准备

- Python 3.10+
- MySQL 8.0+
- 通义千问 API Key（[申请地址](https://dashscope.console.aliyun.com/)）

### 2. 配置环境变量

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

### 3. 初始化数据库

登录 MySQL 后依次执行：

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed_data.sql
```

这将创建数据库、表结构，并填充 2026年1-3月的模拟生产数据（10台设备、8种产品）。

### 4. 安装依赖

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 5. 启动后端服务

```bash
python -m backend.app.main
```

后端API运行在 `http://localhost:8000`，API文档访问 `http://localhost:8000/docs`

### 6. 启动前端

```bash
streamlit run frontend/app.py
```

前端运行在 `http://localhost:8501`

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/chat` | POST | 自然语言查询 |
| `/api/v1/oee/overview` | GET | OEE概览 |
| `/api/v1/oee/trend` | GET | OEE趋势 |
| `/api/v1/oee/equipment-ranking` | GET | 设备排名 |
| `/api/v1/oee/workshop-summary` | GET | 车间汇总 |
| `/api/v1/oee/downtime-analysis` | GET | 停机分析 |
| `/api/v1/oee/loss-analysis` | GET | 损失分析 |

## 自然语言查询示例

- "本月OEE最高的设备是哪台？"
- "一车间3月份的OEE趋势如何？"
- "哪台设备的停机时间最长？"
- "各车间的质量率对比情况"
- "2月份非计划停机的主要原因是什么？"
- "注塑机的可用率和性能率表现"

## OEE 计算公式

```
OEE = 可用率 × 性能率 × 质量率

可用率 = 实际运行时间 / 计划生产时间
性能率 = (理论节拍 × 总产出) / (实际运行时间 × 60)
质量率 = 合格数量 / 总产出数量
```

| 标杆指标 | 世界级水平 |
|----------|-----------|
| OEE | ≥ 85% |
| 可用率 | ≥ 90% |
| 性能率 | ≥ 95% |
| 质量率 | ≥ 99% |
