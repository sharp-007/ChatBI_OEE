import re
import time
import logging
from typing import Any
from sqlalchemy import text
from backend.app.models.database import SessionLocal

logger = logging.getLogger(__name__)


class DatabaseService:
    """数据库查询服务，负责执行SQL并返回结果"""

    FORBIDDEN_KEYWORDS = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "TRUNCATE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    ]

    _schema_cache: str | None = None
    _schema_cache_time: float = 0
    _SCHEMA_CACHE_TTL = 300

    @staticmethod
    def validate_sql(sql: str) -> tuple[bool, str]:
        """校验SQL安全性，仅允许SELECT语句"""
        cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
        cleaned = cleaned.strip().rstrip(";").strip()

        if not cleaned.upper().startswith("SELECT"):
            return False, "仅允许SELECT查询语句"

        upper_sql = cleaned.upper()
        for keyword in DatabaseService.FORBIDDEN_KEYWORDS:
            pattern = rf"\b{keyword}\b"
            if re.search(pattern, upper_sql):
                return False, f"SQL中包含禁止的关键字: {keyword}"

        return True, "OK"

    @staticmethod
    def execute_query(sql: str) -> dict[str, Any]:
        """执行SQL查询并返回结构化结果"""
        is_valid, msg = DatabaseService.validate_sql(sql)
        if not is_valid:
            return {"success": False, "error": msg, "columns": [], "rows": []}

        db = SessionLocal()
        try:
            result = db.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"SQL执行错误: {str(e)}",
                "columns": [],
                "rows": [],
            }
        finally:
            db.close()

    @classmethod
    def get_schema_info(cls) -> str:
        """获取数据库Schema信息（从元数据表动态构建，带TTL缓存）"""
        now = time.time()
        if cls._schema_cache and now - cls._schema_cache_time < cls._SCHEMA_CACHE_TTL:
            return cls._schema_cache

        try:
            schema = cls._build_schema_from_metadata()
            cls._schema_cache = schema
            cls._schema_cache_time = now
            return schema
        except Exception as e:
            logger.warning("元数据表读取失败，回退到硬编码Schema: %s", e)
            return cls._get_hardcoded_schema()

    @classmethod
    def reload_schema_cache(cls):
        """强制刷新Schema缓存（可由管理接口调用）"""
        cls._schema_cache = None
        cls._schema_cache_time = 0

    @staticmethod
    def _build_schema_from_metadata() -> str:
        """从 schema_metadata 表动态构建 Schema 文本，替代硬编码方式"""
        db = SessionLocal()
        try:
            rows = db.execute(text(
                "SELECT table_name, column_name, column_type, description, "
                "sample_values, business_rule, sort_order "
                "FROM schema_metadata WHERE is_important = TRUE "
                "ORDER BY sort_order, id"
            )).fetchall()

            if not rows:
                raise ValueError("schema_metadata表为空")

            tables: dict[str, dict] = {}
            global_rules: list[tuple[int, str]] = []

            for r in rows:
                tname, cname, ctype, desc, samples, rule, sorder = r

                if tname == "_global":
                    rule_text = f"{desc}:\n{rule}" if rule else desc
                    global_rules.append((sorder, rule_text))
                    continue

                if tname not in tables:
                    tables[tname] = {"desc": "", "sort_order": sorder, "columns": []}

                if cname is None:
                    tables[tname]["desc"] = desc
                else:
                    col_line = f"   - {cname}: {ctype}, {desc}"
                    if samples:
                        col_line += f" ({samples})"
                    tables[tname]["columns"].append(col_line)

            parts = ["数据库名: chatbi_oee\n包含以下表:"]

            sorted_tables = sorted(tables.items(), key=lambda x: x[1]["sort_order"])
            for idx, (tname, meta) in enumerate(sorted_tables, 1):
                block = f"\n{idx}. {tname} ({meta['desc']})"
                if meta["columns"]:
                    block += "\n" + "\n".join(meta["columns"])
                parts.append(block)

            global_rules.sort(key=lambda x: x[0])
            for _, rule_text in global_rules:
                parts.append(f"\n{rule_text}")

            return "\n" + "\n".join(parts) + "\n"
        finally:
            db.close()

    @staticmethod
    def _get_hardcoded_schema() -> str:
        """硬编码Schema（降级方案，当元数据表不可用时自动回退）"""
        return """
数据库名: chatbi_oee
包含以下表:

1. equipment (设备主数据表)
   - id: INT, 主键
   - equipment_code: VARCHAR(50), 设备编号 (如 EQ-A01)
   - equipment_name: VARCHAR(100), 设备名称
   - equipment_type: VARCHAR(50), 设备类型 (CNC加工中心/数控车床/注塑机/冲压机/自动组装线/焊接机器人)
   - workshop: VARCHAR(50), 车间 (一车间/二车间/三车间)
   - production_line: VARCHAR(50), 产线 (A线/B线/C线/D线/E线/F线)
   - ideal_cycle_time: DECIMAL(10,2), 理论节拍(秒/件)
   - status: ENUM('running','idle','maintenance','breakdown'), 当前状态

2. product (产品主数据表)
   - id: INT, 主键
   - product_code: VARCHAR(50), 产品编号
   - product_name: VARCHAR(100), 产品名称
   - product_category: VARCHAR(50), 产品类别

3. production_record (生产记录表)
   - id: INT, 主键
   - record_date: DATE, 生产日期
   - shift: VARCHAR(20), 班次 (早班/中班/晚班)
   - equipment_id: INT, 设备ID (关联 equipment.id)
   - product_id: INT, 产品ID (关联 product.id)
   - planned_duration_minutes: INT, 计划生产时长(分钟)
   - actual_run_minutes: DECIMAL(10,2), 实际运行时长(分钟)
   - total_count: INT, 总产出数量
   - good_count: INT, 合格数量
   - defect_count: INT, 不良数量
   - ideal_cycle_time: DECIMAL(10,2), 理论节拍(秒/件)

4. downtime_record (停机记录表)
   - id: INT, 主键
   - record_date: DATE, 日期
   - shift: VARCHAR(20), 班次
   - equipment_id: INT, 设备ID (关联 equipment.id)
   - downtime_type: ENUM('planned','unplanned'), 停机类型 (planned=计划停机, unplanned=非计划停机)
   - downtime_category: VARCHAR(50), 停机分类 (机械故障/电气故障/物料问题/质量问题/换型调整/计划保养)
   - downtime_reason: VARCHAR(200), 停机原因
   - start_time: DATETIME, 开始时间
   - end_time: DATETIME, 结束时间
   - duration_minutes: DECIMAL(10,2), 停机时长(分钟)

5. oee_daily (OEE日汇总视图, 已JOIN了 equipment 和 product 表, 直接查询即可, 无需再JOIN这两张表)
   - record_date: DATE, 生产日期
   - shift: VARCHAR(20), 班次
   - equipment_id: INT, 设备ID (可用于子查询关联 equipment 表获取 equipment_type)
   - equipment_code: VARCHAR(50), 设备编号
   - equipment_name: VARCHAR(100), 设备名称
   - workshop: VARCHAR(50), 车间
   - production_line: VARCHAR(50), 产线
   - product_name: VARCHAR(100), 产品名称
   - planned_duration_minutes: INT, 计划时长
   - actual_run_minutes: DECIMAL, 实际运行时长
   - total_count: INT, 总产出
   - good_count: INT, 合格数
   - defect_count: INT, 不良数
   - availability: DECIMAL, 可用率(%)
   - performance: DECIMAL, 性能率(%)
   - quality: DECIMAL, 质量率(%)
   - oee: DECIMAL, OEE(%)

OEE计算公式:
- 可用率(Availability) = 实际运行时间 / 计划生产时间 × 100%
- 性能率(Performance) = (理论节拍 × 总产出) / (实际运行时间 × 60) × 100%
- 质量率(Quality) = 合格数量 / 总产出数量 × 100%
- OEE = 可用率 × 性能率 × 质量率 / 10000 (因为三项都是百分比)

数据时间范围: 2026-01-01 至 2026-03-31 (工作日)
"""
