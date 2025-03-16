from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
import uuid

from backend.app.core.zhipuai.Conversational_Filtering import ChatService
from backend.app.routes.goods import get_filtered_goods_data

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务
chat_service = ChatService()

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections[session_id] = websocket
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            raise

    def disconnect(self, session_id: str):
        try:
            if session_id in self.active_connections:
                del self.active_connections[session_id]
        except Exception as e:
            logger.error(f"WebSocket断开连接失败: {str(e)}")

    async def send_message(self, session_id: str, message: str):
        try:
            if session_id in self.active_connections:
                await self.active_connections[session_id].send_text(message)
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {str(e)}")

manager = ConnectionManager()

# 请求模型定义
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    filter_only: bool = False

# API路由
@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """对话式筛选API - 普通HTTP请求方式"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        # 使用已过滤的商品数据
        products = await get_filtered_goods_data()

        # 处理用户查询
        result = await chat_service.process_query(request.query, products, session_id)

        # 仅返回筛选结果（适用于某些场景）
        if request.filter_only:
            return {
                "session_id": session_id,
                "filtered_products": result["filtered_products"],
                "filter_reason": result["filter_reason"]
            }

        # 返回完整结果
        return {
            "session_id": session_id,
            "response": result["response"],
            "filtered_products": result["filtered_products"],
            "filter_reason": result["filter_reason"],
            "suggested_filters": result["suggested_filters"]
        }
    except Exception as e:
        logger.error(f"对话处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理查询时出错: {str(e)}")

@router.websocket("/chat/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str = None):
    """对话式筛选API - WebSocket流式响应方式"""
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        await manager.connect(session_id, websocket)

        try:
            # 使用已过滤的商品数据
            products = await get_filtered_goods_data()

            # 发送初始连接信息
            await manager.send_message(
                session_id,
                json.dumps({
                    "type": "connection_established",
                    "session_id": session_id,
                    "total_products": len(products)
                })
            )

            while True:
                try:
                    data = await websocket.receive_text()
                    try:
                        request_data = json.loads(data)
                        query = request_data.get("query", "")

                        if not query:
                            await manager.send_message(
                                session_id,
                                json.dumps({"type": "error", "message": "查询内容不能为空"})
                            )
                            continue

                        # 处理用户查询
                        result = await chat_service.process_query(query, products, session_id)

                        # 发送AI回复
                        await manager.send_message(
                            session_id,
                            json.dumps({
                                "type": "response",
                                "content": result["response"]
                            })
                        )

                        # 发送筛选结果
                        await manager.send_message(
                            session_id,
                            json.dumps({
                                "type": "filtered_products",
                                "products": result["filtered_products"],
                                "reason": result["filter_reason"],
                                "count": len(result["filtered_products"])
                            })
                        )

                        # 发送筛选建议
                        await manager.send_message(
                            session_id,
                            json.dumps({
                                "type": "suggested_filters",
                                "suggestions": result["suggested_filters"]
                            })
                        )

                    except json.JSONDecodeError:
                        await manager.send_message(
                            session_id,
                            json.dumps({"type": "error", "message": "无效的JSON格式"})
                        )
                    except Exception as e:
                        logger.error(f"WebSocket处理错误: {str(e)}")
                        await manager.send_message(
                            session_id,
                            json.dumps({"type": "error", "message": f"处理请求时出错: {str(e)}"})
                        )

                except Exception as e:
                    logger.error(f"接收WebSocket消息失败: {str(e)}")
                    break

        except Exception as e:
            logger.error(f"WebSocket会话处理失败: {str(e)}")
            raise
        finally:
            manager.disconnect(session_id)

    except Exception as e:
        logger.error(f"WebSocket连接初始化失败: {str(e)}")
        raise

@router.get("/suggestions")
async def get_filter_suggestions(query: str = Query(...)):
    """获取筛选建议API"""
    try:
        # 使用已过滤的商品数据
        products = await get_filtered_goods_data()
        suggestions = chat_service.suggest_filters(products, query)

        return {
            "query": query,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"获取筛选建议错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取筛选建议时出错: {str(e)}")