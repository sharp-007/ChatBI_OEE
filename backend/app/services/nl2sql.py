import json
import re
from backend.app.services.llm_service import llm_service
from backend.app.services.db_service import DatabaseService
from backend.app.prompts.nl2sql_prompt import (
    NL2SQL_SYSTEM_PROMPT,
    INTERPRET_SYSTEM_PROMPT,
    CHART_RECOMMEND_PROMPT,
)

MAX_HISTORY_ROUNDS = 5


class NL2SQLService:
    """自然语言转SQL核心服务，支持多轮对话记忆"""

    def __init__(self):
        self.db_service = DatabaseService()

    def _clean_sql(self, raw: str) -> str:
        """清理LLM返回的SQL，去除markdown代码块等格式，修正非标准字符"""
        cleaned = re.sub(r"```sql\s*", "", raw)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.replace("≥", ">=").replace("≤", "<=").replace("≠", "!=")
        cleaned = cleaned.replace("\uff1e\uff1d", ">=").replace("\uff1c\uff1d", "<=")
        cleaned = cleaned.replace("\uff1e", ">").replace("\uff1c", "<")
        cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
        cleaned = cleaned.replace("\u201c", "'").replace("\u201d", "'")
        cleaned = re.sub(r"[≧≩]", ">=", cleaned)
        cleaned = re.sub(r"[≦≨]", "<=", cleaned)
        cleaned = cleaned.strip().rstrip(";") + ";"
        return cleaned

    @staticmethod
    def _build_nl2sql_history(conversation_history: list[dict]) -> list[dict]:
        """将前端对话历史转换为LLM多轮消息格式（仅保留最近N轮）

        每轮包含: 用户问题 + 助手生成的SQL + 查询结果摘要
        这样LLM能理解上下文中的指代和追问。
        """
        rounds = []
        i = 0
        while i < len(conversation_history):
            item = conversation_history[i]
            if item.get("role") == "user":
                user_msg = item["content"]
                assistant_summary = ""
                if i + 1 < len(conversation_history):
                    resp = conversation_history[i + 1]
                    if resp.get("role") == "assistant":
                        parts = []
                        if resp.get("sql"):
                            parts.append(f"生成的SQL: {resp['sql']}")
                        if resp.get("content"):
                            parts.append(f"分析结论: {resp['content'][:200]}")
                        assistant_summary = "\n".join(parts) if parts else resp.get("content", "")
                        i += 1
                rounds.append((user_msg, assistant_summary))
            i += 1

        recent = rounds[-MAX_HISTORY_ROUNDS:]

        messages = []
        for user_msg, assistant_msg in recent:
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})

        return messages

    def text_to_sql(self, question: str,
                    history: list[dict] | None = None) -> str:
        """将自然语言问题转换为SQL，支持多轮上下文"""
        schema_info = DatabaseService.get_schema_info()
        system_prompt = NL2SQL_SYSTEM_PROMPT.format(schema=schema_info)
        sql = llm_service.chat(system_prompt, question, history=history)
        return self._clean_sql(sql)

    def interpret_result(self, question: str, sql: str, rows: list[dict],
                         conversation_history: list[dict] | None = None) -> str:
        """对查询结果进行自然语言解读，包含SQL和对话上下文"""
        data_summary = json.dumps(rows[:50], ensure_ascii=False, default=str)

        context_parts = []
        if conversation_history:
            recent_qa = []
            for msg in conversation_history[-(MAX_HISTORY_ROUNDS * 2):]:
                if msg.get("role") == "user":
                    recent_qa.append(f"用户: {msg['content']}")
                elif msg.get("role") == "assistant" and msg.get("content"):
                    recent_qa.append(f"助手: {msg['content'][:150]}")
            if recent_qa:
                context_parts.append("对话上下文:\n" + "\n".join(recent_qa))

        user_msg = ""
        if context_parts:
            user_msg += "\n".join(context_parts) + "\n\n"
        user_msg += f"当前用户问题: {question}\n\n执行的SQL:\n{sql}\n\n查询结果数据:\n{data_summary}"

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

    def _is_valid_sql(self, sql: str) -> bool:
        """判断LLM返回的内容是否为有效SQL"""
        cleaned = sql.strip().rstrip(";").strip()
        return cleaned.upper().startswith("SELECT")

    def query(self, question: str,
              conversation_history: list[dict] | None = None) -> dict:
        """完整的NL2SQL查询流程，支持多轮对话上下文"""
        llm_history = None
        if conversation_history:
            llm_history = self._build_nl2sql_history(conversation_history)

        sql = self.text_to_sql(question, history=llm_history)

        if not self._is_valid_sql(sql):
            hint = sql.rstrip(";").strip()
            fallback = (
                "您的问题比较宽泛，我无法直接生成查询。您可以试试以下具体问题：\n\n"
                "- 各车间本月OEE对比情况如何？\n"
                "- 哪台设备的OEE最需要改进？\n"
                "- 最近一个月停机时间最长的设备是哪台？\n"
                "- 各设备的可用率、性能率、质量率排名\n"
                "- 不良率最高的产品是什么？"
            )
            return {
                "success": True,
                "sql": "",
                "interpretation": hint if len(hint) > 10 else fallback,
                "chart_config": {"chart_type": "table"},
                "data": {"columns": [], "rows": []},
            }

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

        interpretation = self.interpret_result(question, sql, result["rows"],
                                                conversation_history=conversation_history)
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
