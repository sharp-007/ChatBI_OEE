import json
import re
from backend.app.services.llm_service import llm_service
from backend.app.services.db_service import DatabaseService
from backend.app.prompts.nl2sql_prompt import (
    NL2SQL_SYSTEM_PROMPT,
    INTERPRET_SYSTEM_PROMPT,
    CHART_RECOMMEND_PROMPT,
)


class NL2SQLService:
    """自然语言转SQL核心服务"""

    def __init__(self):
        self.db_service = DatabaseService()
        self.schema_info = DatabaseService.get_schema_info()

    def _clean_sql(self, raw: str) -> str:
        """清理LLM返回的SQL，去除markdown代码块等格式"""
        cleaned = re.sub(r"```sql\s*", "", raw)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip().rstrip(";") + ";"
        return cleaned

    def text_to_sql(self, question: str) -> str:
        """将自然语言问题转换为SQL"""
        system_prompt = NL2SQL_SYSTEM_PROMPT.format(schema=self.schema_info)
        sql = llm_service.chat(system_prompt, question)
        return self._clean_sql(sql)

    def interpret_result(self, question: str, rows: list[dict]) -> str:
        """对查询结果进行自然语言解读"""
        data_summary = json.dumps(rows[:50], ensure_ascii=False, default=str)
        user_msg = f"用户问题: {question}\n\n查询结果数据:\n{data_summary}"
        return llm_service.chat(INTERPRET_SYSTEM_PROMPT, user_msg)

    def recommend_chart(self, question: str, columns: list[str], rows: list[dict]) -> dict:
        """推荐图表类型和配置"""
        sample = json.dumps(rows[:10], ensure_ascii=False, default=str)
        user_msg = (
            f"用户问题: {question}\n"
            f"数据列: {columns}\n"
            f"示例数据:\n{sample}"
        )
        raw = llm_service.chat(CHART_RECOMMEND_PROMPT, user_msg)

        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        return {"chart_type": "table", "x_field": "", "y_field": "", "title": "查询结果"}

    def query(self, question: str) -> dict:
        """完整的NL2SQL查询流程: 问题 -> SQL -> 执行 -> 解读 -> 图表推荐"""
        sql = self.text_to_sql(question)

        result = self.db_service.execute_query(sql)

        if not result["success"]:
            return {
                "success": False,
                "sql": sql,
                "error": result["error"],
                "interpretation": f"查询执行失败: {result['error']}",
                "chart_config": {"chart_type": "table"},
                "data": {"columns": [], "rows": []},
            }

        interpretation = self.interpret_result(question, result["rows"])
        chart_config = self.recommend_chart(question, result["columns"], result["rows"])

        return {
            "success": True,
            "sql": sql,
            "interpretation": interpretation,
            "chart_config": chart_config,
            "data": {
                "columns": result["columns"],
                "rows": result["rows"],
                "row_count": result["row_count"],
            },
        }


nl2sql_service = NL2SQLService()
