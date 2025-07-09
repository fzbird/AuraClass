#!/usr/bin/env python3
"""
发送测试通知的脚本
用法: python send_test_notification.py [用户ID] [通知内容]
"""

import sys
import asyncio
import httpx
import json
import os
import datetime

# 获取凭证
async def get_token():
    """登录并获取token"""
    url = "http://localhost:8200/api/v1/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get("data", {}).get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None

# 发送测试通知
async def send_notification(token, user_id, content):
    """发送通知"""
    url = "http://localhost:8200/api/v1/notifications"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "title": f"测试通知 - {current_time}",
        "content": content,
        "notification_type": "system",
        "recipient_user_id": int(user_id),
        "is_read": False
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        if response.status_code in (200, 201):
            result = response.json()
            print(f"通知发送成功: {result}")
        else:
            print(f"通知发送失败: {response.status_code} - {response.text}")

async def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python send_test_notification.py [用户ID] [通知内容]")
        return
    
    user_id = sys.argv[1]
    content = sys.argv[2]
    
    token = await get_token()
    if not token:
        print("获取token失败")
        return
    
    await send_notification(token, user_id, content)

if __name__ == "__main__":
    asyncio.run(main()) 