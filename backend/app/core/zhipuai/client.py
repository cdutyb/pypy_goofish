from zhipuai import ZhipuAI
import json
import logging

logger = logging.getLogger(__name__)


class GLMClient:
    def __init__(self, api_key=None):
        """初始化智谱AI客户端

        Args:
            api_key: 智谱AI API密钥，如未提供则从环境变量获取
        """
        if not api_key:
            api_key = "5abc38d09bc340b29ca44f80143f9bb3.ONUBxMKyM5R37uEf"  # 替换成您的API密钥

        self.client = ZhipuAI(api_key=api_key)
        self.model = "glm-4-flash"  # 使用GLM-4-Flash模型

    def generate_response(self, messages):
        """同步调用智谱AI接口生成回复

        Args:
            messages: 对话历史消息列表

        Returns:
            生成的回复文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"智谱AI API调用错误: {str(e)}")
            return f"很抱歉，服务出现了问题: {str(e)}"

    def function_call(self, messages, tools, function_name):
        """通用函数调用接口"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": function_name}}
            )

            result = None
            if response.choices and response.choices[0].message.tool_calls:
                result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

            return result
        except Exception as e:
            logger.error(f"函数调用错误: {str(e)}")
            return None