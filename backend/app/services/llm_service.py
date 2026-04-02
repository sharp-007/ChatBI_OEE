import dashscope
from dashscope import Generation
from backend.app.config import settings


class LLMService:
    """通义千问 LLM 调用服务"""

    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.LLM_MODEL

    def chat(self, system_prompt: str, user_message: str,
             history: list[dict] | None = None) -> str:
        """调用通义千问进行对话，支持多轮历史消息"""
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message",
                temperature=0.1,
                max_tokens=2000,
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content.strip()
            else:
                return f"LLM调用失败: {response.code} - {response.message}"

        except Exception as e:
            return f"LLM服务异常: {str(e)}"


llm_service = LLMService()
