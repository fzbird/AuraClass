import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_notification_websocket(token, user_id):
    """测试通知WebSocket连接"""
    uri = f"ws://localhost:8200/ws/notifications/{user_id}?token={token}"
    
    try:
        print(f"正在连接到通知WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print("连接成功！")
            
            # 发送确认消息
            ack_message = {
                "type": "ack",
                "notification_id": 1  # 替换为实际通知ID
            }
            await websocket.send(json.dumps(ack_message))
            print(f"发送确认消息: {ack_message}")
            
            # 等待接收消息
            print("等待接收消息...")
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(response)
                    print(f"收到消息: {data}")
                except asyncio.TimeoutError:
                    print("超时，没有收到消息")
                    break
                except Exception as e:
                    print(f"接收消息出错: {str(e)}")
                    break
    except Exception as e:
        print(f"连接失败: {str(e)}")

async def test_ai_assistant_websocket(token, user_id):
    """测试AI助手WebSocket连接"""
    uri = f"ws://localhost:8200/ws/ai-assistant/{user_id}?token={token}"
    
    try:
        print(f"正在连接到AI助手WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print("连接成功！")
            
            # 发送查询消息
            query_message = {
                "type": "query",
                "data": {
                    "query_text": "你好，这是一个测试消息"
                }
            }
            await websocket.send(json.dumps(query_message))
            print(f"发送查询消息: {query_message}")
            
            # 等待接收响应
            print("等待接收响应...")
            for _ in range(5):  # 最多等待5个响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(response)
                    print(f"收到响应: {data}")
                    
                    # 如果收到了响应，再发送一个建议请求
                    if data.get("type") == "response":
                        suggestion_message = {
                            "type": "suggest",
                            "data": {
                                "prefix": "如何"
                            }
                        }
                        await websocket.send(json.dumps(suggestion_message))
                        print(f"发送建议请求: {suggestion_message}")
                except asyncio.TimeoutError:
                    print("超时，没有收到响应")
                    break
                except Exception as e:
                    print(f"接收响应出错: {str(e)}")
                    break
    except Exception as e:
        print(f"连接失败: {str(e)}")

async def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python test_websocket.py <token> <user_id> [notification|ai|all]")
        return
    
    token = sys.argv[1]
    user_id = sys.argv[2]
    test_type = sys.argv[3] if len(sys.argv) > 3 else "all"
    
    if test_type in ["notification", "all"]:
        print("\n=== 测试通知WebSocket ===")
        await test_notification_websocket(token, user_id)
    
    if test_type in ["ai", "all"]:
        print("\n=== 测试AI助手WebSocket ===")
        await test_ai_assistant_websocket(token, user_id)

if __name__ == "__main__":
    asyncio.run(main()) 