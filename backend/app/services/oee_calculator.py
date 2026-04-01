from typing import Any, Optional
from sqlalchemy import text
from backend.app.models.database import SessionLocal


class OEECalculator:
    """OEE 计算引擎，提供多维度OEE指标计算"""

    @staticmethod
    def _execute(sql: str, params: Optional[dict] = None) -> list[dict]:
        db = SessionLocal()
        try:
            result = db.execute(text(sql), params or {})
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in result.fetchall()]
        finally:
            db.close()

    @classmethod
    def get_overall_oee(cls, start_date: str, end_date: str) -> dict[str, Any]:
        """获取整体OEE概览"""
        sql = """
            SELECT
                ROUND(AVG(availability), 2) AS avg_availability,
                ROUND(AVG(performance), 2) AS avg_performance,
                ROUND(AVG(quality), 2) AS avg_quality,
                ROUND(AVG(oee), 2) AS avg_oee,
                COUNT(*) AS record_count,
                SUM(total_count) AS total_output,
                SUM(good_count) AS total_good,
                SUM(defect_count) AS total_defect
            FROM oee_daily
            WHERE record_date BETWEEN :start_date AND :end_date
        """
        rows = cls._execute(sql, {"start_date": start_date, "end_date": end_date})
        return rows[0] if rows else {}

    @classmethod
    def get_oee_trend(cls, start_date: str, end_date: str,
                      group_by: str = "day") -> list[dict]:
        """获取OEE趋势数据"""
        if group_by == "week":
            date_expr = "DATE_FORMAT(record_date, '%Y-W%u')"
            date_alias = "周"
        elif group_by == "month":
            date_expr = "DATE_FORMAT(record_date, '%Y-%m')"
            date_alias = "月份"
        else:
            date_expr = "record_date"
            date_alias = "日期"

        sql = f"""
            SELECT
                {date_expr} AS `{date_alias}`,
                ROUND(AVG(availability), 2) AS `可用率`,
                ROUND(AVG(performance), 2) AS `性能率`,
                ROUND(AVG(quality), 2) AS `质量率`,
                ROUND(AVG(oee), 2) AS `OEE`
            FROM oee_daily
            WHERE record_date BETWEEN :start_date AND :end_date
            GROUP BY {date_expr}
            ORDER BY {date_expr}
        """
        return cls._execute(sql, {"start_date": start_date, "end_date": end_date})

    @classmethod
    def get_equipment_ranking(cls, start_date: str, end_date: str) -> list[dict]:
        """获取设备OEE排名"""
        sql = """
            SELECT
                equipment_code AS `设备编号`,
                equipment_name AS `设备名称`,
                workshop AS `车间`,
                production_line AS `产线`,
                ROUND(AVG(availability), 2) AS `可用率`,
                ROUND(AVG(performance), 2) AS `性能率`,
                ROUND(AVG(quality), 2) AS `质量率`,
                ROUND(AVG(oee), 2) AS `OEE`,
                SUM(total_count) AS `总产出`,
                SUM(good_count) AS `合格数`
            FROM oee_daily
            WHERE record_date BETWEEN :start_date AND :end_date
            GROUP BY equipment_code, equipment_name, workshop, production_line
            ORDER BY `OEE` DESC
        """
        return cls._execute(sql, {"start_date": start_date, "end_date": end_date})

    @classmethod
    def get_workshop_summary(cls, start_date: str, end_date: str) -> list[dict]:
        """获取车间维度汇总"""
        sql = """
            SELECT
                workshop AS `车间`,
                ROUND(AVG(availability), 2) AS `可用率`,
                ROUND(AVG(performance), 2) AS `性能率`,
                ROUND(AVG(quality), 2) AS `质量率`,
                ROUND(AVG(oee), 2) AS `OEE`,
                SUM(total_count) AS `总产出`,
                SUM(good_count) AS `合格数`,
                SUM(defect_count) AS `不良数`
            FROM oee_daily
            WHERE record_date BETWEEN :start_date AND :end_date
            GROUP BY workshop
            ORDER BY `OEE` DESC
        """
        return cls._execute(sql, {"start_date": start_date, "end_date": end_date})

    @classmethod
    def get_downtime_analysis(cls, start_date: str, end_date: str) -> dict[str, Any]:
        """获取停机分析"""
        by_category_sql = """
            SELECT
                downtime_category AS `停机分类`,
                downtime_type AS `停机类型`,
                COUNT(*) AS `停机次数`,
                ROUND(SUM(duration_minutes), 0) AS `总停机时长_分钟`,
                ROUND(AVG(duration_minutes), 1) AS `平均停机时长_分钟`
            FROM downtime_record
            WHERE record_date BETWEEN :start_date AND :end_date
            GROUP BY downtime_category, downtime_type
            ORDER BY `总停机时长_分钟` DESC
        """

        by_equipment_sql = """
            SELECT
                e.equipment_name AS `设备名称`,
                e.workshop AS `车间`,
                COUNT(*) AS `停机次数`,
                ROUND(SUM(d.duration_minutes), 0) AS `总停机时长_分钟`
            FROM downtime_record d
            JOIN equipment e ON d.equipment_id = e.id
            WHERE d.record_date BETWEEN :start_date AND :end_date
            GROUP BY e.equipment_name, e.workshop
            ORDER BY `总停机时长_分钟` DESC
        """

        params = {"start_date": start_date, "end_date": end_date}
        return {
            "by_category": cls._execute(by_category_sql, params),
            "by_equipment": cls._execute(by_equipment_sql, params),
        }

    @classmethod
    def get_loss_analysis(cls, start_date: str, end_date: str) -> list[dict]:
        """获取六大损失分析"""
        sql = """
            SELECT
                equipment_name AS `设备名称`,
                workshop AS `车间`,
                ROUND(AVG(planned_duration_minutes - actual_run_minutes), 1) AS `可用性损失_分钟`,
                ROUND(AVG(actual_run_minutes * 60 - ideal_cycle_time * total_count) / 60, 1) AS `性能损失_分钟`,
                ROUND(AVG(defect_count * ideal_cycle_time) / 60, 1) AS `质量损失_分钟`,
                ROUND(AVG(planned_duration_minutes), 1) AS `计划时间_分钟`
            FROM oee_daily
            WHERE record_date BETWEEN :start_date AND :end_date
            GROUP BY equipment_name, workshop
            ORDER BY `可用性损失_分钟` DESC
        """
        return cls._execute(sql, {"start_date": start_date, "end_date": end_date})
