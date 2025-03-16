import json
import logging
from .client import GLMClient

logger = logging.getLogger(__name__)


class ChatService:
    """负责对话式商品筛选功能"""

    def __init__(self, api_key=None):
        self.client = GLMClient(api_key)
        self.conversation_history = {}

    async def process_query(self, query, products, session_id=None):
        """处理用户查询并提供筛选结果"""
        if not session_id:
            session_id = "default"

        # 获取历史记录
        history = self.conversation_history.get(session_id, [])

        # 初始化会话
        if not history:
            history = [{
                "role": "system",
                "content": "你是一个商品助手，能够根据用户需求筛选和推荐商品。请理解用户需求，给出回复和筛选结果。"
            }]

        # 添加用户查询
        history.append({"role": "user", "content": query})

        # 添加商品数据提示
        if len(history) <= 3:
            product_info = f"当前有{len(products)}件商品可供筛选。"
            history.append({"role": "system", "content": product_info})
            history.append({"role": "user", "content": f"请基于这些商品数据回答我的问题。我的问题是：{query}"})

        # 获取AI回复
        response_text = self.client.generate_response(history)

        # 添加回复到历史
        history.append({"role": "assistant", "content": response_text})

        # 更新会话历史
        self.conversation_history[session_id] = history[-10:]

        # 获取筛选结果
        filtered_products, filter_reason = self.filter_products_by_query(products, query)

        # 获取推荐筛选条件
        suggested_filters = self.suggest_filters(products, query)

        return {
            "response": response_text,
            "filtered_products": filtered_products,
            "filter_reason": filter_reason,
            "suggested_filters": suggested_filters
        }

    def filter_products_by_query(self, products, query):
        """根据查询筛选商品"""
        tools = [
            {
                "name": "filter_products",
                "description": "根据用户需求筛选商品",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filtered_indices": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "符合筛选条件的商品索引列表"
                        },
                        "filter_reason": {
                            "type": "string",
                            "description": "筛选理由说明"
                        }
                    },
                    "required": ["filtered_indices"]
                }
            }
        ]

        messages = [
            {"role": "system", "content": "你是商品筛选助手，根据用户需求筛选并解释筛选理由。"},
            {"role": "user", "content": f"用户需求: {query}\n商品列表: {json.dumps(products, ensure_ascii=False)}"}
        ]

        try:
            result = self.client.function_call(messages, tools, "filter_products")
            if result:
                filtered_indices = result.get("filtered_indices", [])
                filter_reason = result.get("filter_reason", "")
                filtered_products = [products[i] for i in filtered_indices if 0 <= i < len(products)]
                return filtered_products, filter_reason

            return products, "筛选失败，显示所有商品"
        except Exception as e:
            logger.error(f"商品筛选错误: {str(e)}")
            return products, f"筛选出错: {str(e)}"

    def suggest_filters(self, products, query):
        """推荐相关筛选条件"""
        tools = [
            {
                "name": "suggest_filters",
                "description": "推荐商品筛选条件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "suggested_filters": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "建议的筛选条件，每个条件为一短句"
                        }
                    },
                    "required": ["suggested_filters"]
                }
            }
        ]

        messages = [
            {"role": "system", "content": "你是商品筛选助手，推荐3-5个相关的筛选条件。"},
            {"role": "user", "content": f"基于用户查询'{query}'和这些商品，推荐相关的筛选条件和关键词。"}
        ]

        try:
            result = self.client.function_call(messages, tools, "suggest_filters")
            if result:
                return result.get("suggested_filters", [])
            return []
        except Exception as e:
            logger.error(f"获取筛选建议错误: {str(e)}")
            return []