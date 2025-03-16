import json
import logging
from .client import GLMClient

logger = logging.getLogger(__name__)


class SemanticFilter:
    """负责商品的语义过滤，用于预处理展示前的商品"""

    def __init__(self, api_key=None):
        self.client = GLMClient(api_key)

    def filter_invalid_products(self, products):
        """过滤无效商品(已下架、勿拍等)"""
        tools = [
            {
                "name": "filter_valid_products",
                "description": "过滤有效商品",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "valid_indices": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "有效商品的索引列表"
                        },
                        "invalid_count": {
                            "type": "integer",
                            "description": "无效商品数量"
                        }
                    },
                    "required": ["valid_indices"]
                }
            }
        ]

        messages = [
            {"role": "system",
             "content": "你需要从商品列表中过滤掉无效商品，包括标题中含有'已下架'、'已售罄'、'已出勿拍'、'回收'等类似非正常出售状态的商品。"},
            {"role": "user",
             "content": f"请检查以下商品列表，返回有效商品的索引列表:\n{json.dumps(products, ensure_ascii=False)}"}
        ]

        try:
            result = self.client.function_call(messages, tools, "filter_valid_products")
            if result:
                valid_indices = result.get("valid_indices", list(range(len(products))))
                valid_products = [products[i] for i in valid_indices if 0 <= i < len(products)]
                invalid_count = len(products) - len(valid_products)
                return valid_products, invalid_count

            return products, 0
        except Exception as e:
            logger.error(f"语义过滤错误: {str(e)}")
            return products, 0