from typing import Any, List, Optional, Dict
from datetime import datetime, timezone
import asyncio
import hashlib
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import json
import os
from pathlib import Path as FilePath

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.models.user import User
from app.models.ai_conversation import AIMessage  # 添加数据库模型导入
from app.crud.ai_conversation import conversation as conversation_crud, message as message_crud
from app.schemas.ai_conversation import (
    Conversation, ConversationList, ConversationCreate, 
    ConversationUpdate, Message, MessageCreate
)
from app.services.ai_service import ai_assistant
from app.core.config import settings
from app.services.upload_service import upload_service
from app.crud.base import CRUDBase
from app.db.session import safe_db_transaction, get_session_context, async_session

# 消息提交缓存，用于防止重复提交
message_submission_cache: Dict[str, float] = {}
# 添加请求ID缓存，避免重复处理相同请求
request_id_cache: Dict[str, Dict] = {}
# 添加消息创建锁，确保消息按顺序创建
message_creation_locks: Dict[int, str] = {}

# 简单的响应模型
class ResponseBase(BaseModel):
    status: str
    message: Optional[str] = None

router = APIRouter()

@router.post("/query")
async def create_ai_query(
    *,
    db: AsyncSession = Depends(get_db),
    query_text: str = Body(...),
    context_data: Optional[Dict[str, Any]] = Body(None),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/query", method="POST")
) -> Any:
    """
    创建新的AI查询（HTTP方式，用于不支持WebSocket的场景）
    """
    result = await ai_assistant.process_query(
        db,
        user_id=current_user.id,
        query_text=query_text,
        context_data=context_data
    )
    
    return result

@router.get("/suggestions")
async def get_query_suggestions(
    db: AsyncSession = Depends(get_db),
    prefix: str = Query(..., min_length=1),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/suggestions", method="GET")
) -> Any:
    """
    获取查询建议（HTTP方式）
    """
    suggestions = await ai_assistant.get_suggestions(
        db,
        user_id=current_user.id,
        prefix=prefix
    )
    
    return {
        "suggestions": suggestions
    }

# 对话相关端点
@router.get("/conversations", response_model=List[Conversation])
async def read_conversations(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations", method="GET")
) -> Any:
    """
    获取用户的所有对话
    """
    conversations = await conversation_crud.get_user_conversations(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return conversations

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_in: ConversationCreate = Body(...),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations", method="POST")
) -> Any:
    """
    创建新对话
    """
    conversation = await conversation_crud.create_conversation(
        db, 
        obj_in=conversation_in, 
        user_id=current_user.id
    )
    
    return conversation

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def read_conversation(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}", method="GET")
) -> Any:
    """
    获取指定对话
    """
    conversation = await conversation_crud.get(db, id=conversation_id)
    
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_id: int = Path(..., gt=0),
    conversation_in: ConversationUpdate = Body(...),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}", method="PUT")
) -> Any:
    """
    更新对话标题
    """
    conversation = await conversation_crud.get(db, id=conversation_id)
    
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = await conversation_crud.update_conversation_title(
        db, 
        conversation_id=conversation_id, 
        title=conversation_in.title or "未命名对话",
        user_id=current_user.id
    )
    
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}", method="DELETE")
) -> Any:
    """
    删除对话
    """
    conversation = await conversation_crud.get(db, id=conversation_id)
    
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    deleted = await conversation_crud.delete_conversation(
        db, 
        conversation_id=conversation_id, 
        user_id=current_user.id
    )
    
    if not deleted:
        raise HTTPException(status_code=400, detail="Failed to delete conversation")
    
    return {"status": "success"}

# 消息相关端点
@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def read_messages(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}/messages", method="GET")
) -> Any:
    """
    获取对话中的所有消息
    """
    conversation = await conversation_crud.get(db, id=conversation_id)
    
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await message_crud.get_conversation_messages(
        db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit
    )
    
    # 转换为前端期望的格式
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "conversation_id": msg.conversation_id,
            "timestamp": msg.created_at,
            "processing_time": msg.processing_time,
            "use_local_model": msg.use_local_model,
            "model_name": msg.model_name
        })
    
    return result

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    *,
    db: AsyncSession = Depends(get_db),
    conversation_id: int = Path(..., gt=0),
    request: Request,
    content: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    role: str = Form("user"),
    useLocalModel: Optional[bool] = Form(True),
    modelName: Optional[str] = Form("gemma3:27b"),
    useThinkMode: Optional[bool] = Form(True),
    waitForResponse: Optional[bool] = Form(False),  # 添加等待响应参数
    request_id: Optional[str] = Query(None),  # 添加请求ID参数
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}/messages", method="POST")
) -> Any:
    """
    创建新消息并添加到对话中，可选择等待AI响应完成
    """
    # 打印请求参数以便调试
    request_id = request_id or str(uuid.uuid4())
    print(f"[{request_id}] 接收消息参数: conversation_id={conversation_id}, content={content}, role={role}")
    print(f"[{request_id}] 模型参数: useLocalModel={useLocalModel}, modelName={modelName}, useThinkMode={useThinkMode}, waitForResponse={waitForResponse}")
    
    # 如果提供了外部请求ID，检查是否已处理过相同请求
    if request_id in request_id_cache:
        cached_data = request_id_cache[request_id]
        print(f"[{request_id}] 检测到重复请求ID，返回缓存结果")
        return cached_data['response']
    
    # 安全获取用户ID，确保不会触发SQLAlchemy懒加载
    try:
        user_id = current_user.id
    except Exception as e:
        print(f"[{request_id}] 获取用户ID时出错: {str(e)}")
        # 尝试直接从current_user对象获取ID
        user_id = getattr(current_user, 'id', None)
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="无法获取用户信息"
            )
    
    # 检查会话锁
    conversation_lock_key = f"conversation_lock_{conversation_id}"
    current_lock = message_creation_locks.get(conversation_id)
    if current_lock:
        # 检查锁是否在5秒内创建，如果是则拒绝请求
        lock_parts = current_lock.split('_')
        if len(lock_parts) >= 2:
            try:
                lock_time = float(lock_parts[0])
                if time.time() - lock_time < 5:
                    print(f"[{request_id}] 会话 {conversation_id} 已被锁定，拒绝请求")
                    raise HTTPException(
                        status_code=429,
                        detail="请稍后再试，已有处理中的请求"
                    )
            except ValueError:
                pass  # 锁格式无效，继续处理
    
    # 设置新锁
    new_lock = f"{time.time()}_{request_id}"
    message_creation_locks[conversation_id] = new_lock
    print(f"[{request_id}] 为会话 {conversation_id} 设置锁: {new_lock}")
    
    # 处理JSON请求体的情况
    if content is None or content.strip() == "":
        # 尝试从请求体获取content（针对JSON请求）
        try:
            body_bytes = await request.body()
            if body_bytes:
                # 检测请求体内容类型
                content_type = request.headers.get("content-type", "").lower()
                
                # 处理JSON请求体
                if "application/json" in content_type:
                    try:
                        json_body = json.loads(body_bytes)
                        if "content" in json_body and json_body["content"]:
                            content = json_body["content"]
                            print(f"[{request_id}] 从JSON请求体获取content: {content}")
                            
                            # 如果JSON中包含其他参数，也获取
                            if "role" in json_body:
                                role = json_body["role"]
                            if "useLocalModel" in json_body:
                                useLocalModel = json_body["useLocalModel"]
                            if "modelName" in json_body:
                                modelName = json_body["modelName"]
                            if "useThinkMode" in json_body:
                                useThinkMode = json_body["useThinkMode"]
                    except json.JSONDecodeError:
                        print(f"[{request_id}] JSON解析失败")
                else:
                    print(f"[{request_id}] 请求体Content-Type: {content_type}")
                    
                    # 尝试直接解析请求体
                    try:
                        body = await request.json()
                        if "content" in body and body["content"]:
                            content = body["content"]
                            print(f"[{request_id}] 从请求体获取content: {content}")
                    except:
                        print(f"[{request_id}] 无法解析请求体为JSON")
                        
                        # 如果是FormData请求，尝试从form字段获取
                        try:
                            form = await request.form()
                            if "content" in form and form["content"]:
                                content = form["content"]
                                print(f"[{request_id}] 从表单获取content: {content}")
                        except:
                            print(f"[{request_id}] 无法解析表单数据")
        except Exception as e:
            print(f"[{request_id}] 解析请求体时出错: {str(e)}")
    
    # 确保content至少是空字符串而不是None
    content = content or ""
    print(f"[{request_id}] 最终使用的content: {content}")
    
    # 创建请求唯一标识，使用已安全获取的user_id
    request_hash = hashlib.md5(f"{conversation_id}-{content}-{role}-{user_id}-{modelName}".encode()).hexdigest()
    current_time = datetime.now(timezone.utc).timestamp()
    
    # 检查是否有相同的请求正在处理或已处理
    if request_hash in request_id_cache:
        cached_data = request_id_cache[request_hash]
        # 如果5秒内收到相同请求，直接返回缓存结果
        if current_time - cached_data['timestamp'] < 5:
            print(f"[{request_id}] 检测到完全相同的请求: {request_hash}, 返回缓存结果")
            # 释放锁
            if message_creation_locks.get(conversation_id) == new_lock:
                del message_creation_locks[conversation_id]
                print(f"[{request_id}] 释放会话锁: {conversation_id}")
            return cached_data['response']
    
    # 防止重复提交检查 - 增强检查逻辑
    cache_key = f"{conversation_id}-{content}-{role}"
    
    if cache_key in message_submission_cache:
        # 如果5秒内有相同内容的请求，视为重复提交
        last_time = message_submission_cache[cache_key]
        if current_time - last_time < 5:
            print(f"[{request_id}] 检测到重复提交: {cache_key}, 距上次: {current_time - last_time}秒")
            
            # 创建一个新的干净会话来检查最近消息
            async with safe_db_transaction() as clean_db:
                # 获取最近的一条消息返回
                recent_messages = await message_crud.get_conversation_messages(
                    clean_db, conversation_id=conversation_id, limit=10
                )
                
                # 遍历查找内容匹配的消息
                for recent_message in recent_messages:
                    if (recent_message.role == role and 
                        recent_message.content.startswith(content) and
                        # Fix timezone handling in timestamp comparison
                        (current_time - recent_message.created_at.replace(tzinfo=timezone.utc).timestamp()) < 10):
                        print(f"[{request_id}] 找到匹配的消息ID: {recent_message.id}")
                        # 直接返回消息模型，避免模型转换问题
                        response = {
                            "id": recent_message.id,
                            "role": recent_message.role,
                            "content": recent_message.content,
                            "conversation_id": recent_message.conversation_id,
                            "timestamp": recent_message.created_at,
                            "processing_time": recent_message.processing_time,
                            "use_local_model": recent_message.use_local_model,
                            "model_name": recent_message.model_name
                        }
                        # 缓存结果
                        request_id_cache[request_hash] = {
                            'timestamp': current_time,
                            'response': response
                        }
                        # 缓存请求ID结果
                        if request_id:
                            request_id_cache[request_id] = {
                                'timestamp': current_time,
                                'response': response
                            }
                        # 释放锁
                        if message_creation_locks.get(conversation_id) == new_lock:
                            del message_creation_locks[conversation_id]
                            print(f"[{request_id}] 释放会话锁: {conversation_id}")
                        return response
    
    # 更新缓存
    message_submission_cache[cache_key] = current_time
    
    # 初始化文件内容为空字符串
    file_content = ""
    
    try:
        # 使用安全的事务上下文，确保每个操作都在干净的会话中执行
        async with safe_db_transaction() as transaction_db:
            # 检查是否已存在相同内容和时间的消息（额外防止重复）
            existing_messages = await message_crud.get_conversation_messages(
                transaction_db, conversation_id=conversation_id, limit=5
            )
            
            current_time_utc = datetime.now(timezone.utc)
            
            for existing_msg in existing_messages:
                # Check if there's a very similar recent message (within last 3 seconds)
                if (existing_msg.role == role and 
                    existing_msg.content == content and
                    # Fix timezone-aware vs naive datetime issue
                    (current_time_utc.replace(tzinfo=None) - existing_msg.created_at.replace(tzinfo=None)).total_seconds() < 3):
                    print(f"[{request_id}] 找到非常相似的最近消息: {existing_msg.id}")
                    response = {
                        "id": existing_msg.id,
                        "role": existing_msg.role,
                        "content": existing_msg.content,
                        "conversation_id": existing_msg.conversation_id,
                        "timestamp": existing_msg.created_at,
                        "processing_time": existing_msg.processing_time,
                        "use_local_model": existing_msg.use_local_model,
                        "model_name": existing_msg.model_name
                    }
                    # 缓存结果
                    request_id_cache[request_hash] = {
                        'timestamp': current_time,
                        'response': response
                    }
                    # 缓存请求ID结果
                    if request_id:
                        request_id_cache[request_id] = {
                            'timestamp': current_time,
                            'response': response
                        }
                    # 释放锁
                    if message_creation_locks.get(conversation_id) == new_lock:
                        del message_creation_locks[conversation_id]
                        print(f"[{request_id}] 释放会话锁: {conversation_id}")
                    return response
            
            # 使用显式异步查询确保会话存在
            conversation_query = await transaction_db.execute(
                select(conversation_crud.model).where(
                    conversation_crud.model.id == conversation_id,
                    conversation_crud.model.user_id == user_id
                )
            )
            conversation = conversation_query.scalar_one_or_none()
            
            if not conversation:
                # 释放锁
                if message_creation_locks.get(conversation_id) == new_lock:
                    del message_creation_locks[conversation_id]
                    print(f"[{request_id}] 释放会话锁(会话不存在): {conversation_id}")
                raise HTTPException(
                    status_code=404,
                    detail="会话不存在或无权访问"
                )

            # 创建新消息对象
            db_message = AIMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                use_local_model=useLocalModel,
                model_name=modelName,
                created_at=current_time_utc
            )
            
            # 添加到数据库
            transaction_db.add(db_message)
            await transaction_db.flush()  # 使用flush而不是立即commit，保持事务一致性
            
            print(f"[{request_id}] 创建的消息ID: {db_message.id}, 内容: {db_message.content}, 时间: {db_message.created_at}")
    
            # 处理文件上传
            file_attachments = []
            if files:
                try:
                    # 验证文件数量
                    if len(files) > settings.MAX_FILES_PER_REQUEST:
                        raise HTTPException(
                            status_code=400,
                            detail=f"最多允许上传 {settings.MAX_FILES_PER_REQUEST} 个文件"
                        )
                        
                    for file in files:
                        if file and file.filename:
                            # 使用上传服务保存文件，通过entity_type和entity_id关联到消息
                            upload = await upload_service.save_upload(
                                db=transaction_db,
                                file=file,
                                module="ai-assistant",
                                uploader_id=user_id,
                                entity_type="ai_message",
                                entity_id=db_message.id,
                                is_public=0
                            )
                            
                            # 添加文件信息到消息内容
                            if upload.file_type.startswith("image/"):
                                file_content += f"\n[图片: {upload.original_filename}|{upload.file_url}]"
                            else:
                                file_content += f"\n[文件: {upload.original_filename}|{upload.file_url}]"
                            
                            # 收集附件信息用于响应
                            file_attachments.append({
                                "filename": upload.original_filename,
                                "file_path": upload.file_path,
                                "file_type": upload.file_type,
                                "file_size": upload.file_size,
                                "file_url": upload.file_url,
                                "upload_id": upload.id
                            })
                except Exception as e:
                    print(f"[{request_id}] 文件处理错误: {str(e)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件上传失败: {str(e)}"
                    )
            
            # 合并内容
            merged_content = content or ""
            if file_content:
                merged_content = merged_content + file_content
            
            # 更新消息内容
            if merged_content != db_message.content:
                db_message.content = merged_content
                await transaction_db.flush()
            
            # 更新对话的更新时间
            conversation.updated_at = current_time_utc
            
            # transaction_db事务自动提交(async with会处理)
        
        # 事务完成，准备响应
        response = {
            "id": db_message.id,
            "role": db_message.role,
            "content": db_message.content,
            "conversation_id": db_message.conversation_id,
            "timestamp": db_message.created_at,
            "processing_time": db_message.processing_time,
            "use_local_model": db_message.use_local_model,
            "model_name": db_message.model_name
        }
        
        # 如果有附件，添加到响应中
        if file_attachments:
            response["attachments"] = file_attachments
        
        # 缓存响应结果以便重复请求时返回
        request_id_cache[request_hash] = {
            'timestamp': current_time,
            'response': response
        }
        
        # 如果提供了请求ID，也缓存结果
        if request_id:
            request_id_cache[request_id] = {
                'timestamp': current_time,
                'response': response
            }
        
        # 清理缓存，只保留最近1小时的缓存
        cleanup_time = current_time - 3600  # 一小时前
        expired_keys = [k for k, v in request_id_cache.items() if v['timestamp'] < cleanup_time]
        for k in expired_keys:
            del request_id_cache[k]
        
        # 如果是用户消息，创建并启动AI响应任务
        if role == "user":
            if waitForResponse:
                # 直接等待AI响应完成并返回
                try:
                    print(f"[{request_id}] 等待AI响应完成...")
                    # 在同一个事务中处理AI响应
                    ai_response = await ai_assistant.process_query(
                        db,
                        user_id=user_id,
                        query_text=db_message.content,
                        context_data={
                            "conversation_id": conversation_id,
                            "useLocalModel": useLocalModel,
                            "modelName": modelName,
                            "useThinkMode": useThinkMode,
                            # 获取历史消息作为上下文
                            "messages": [
                                {"role": msg.role, "content": msg.content} 
                                for msg in await message_crud.get_conversation_messages(
                                    db, conversation_id=conversation_id, limit=10
                                )
                            ]
                        },
                        timeout=55  # 设置稍短的超时，确保API响应不会超过60秒
                    )
                    
                    # 获取AI响应消息
                    ai_messages = await message_crud.get_newest_message(
                        db, conversation_id=conversation_id, role="assistant"
                    )
                    
                    if ai_messages:
                        print(f"[{request_id}] AI响应已完成，返回用户消息和AI响应")
                        # 释放锁
                        if message_creation_locks.get(conversation_id) == new_lock:
                            del message_creation_locks[conversation_id]
                            print(f"[{request_id}] 释放会话锁: {conversation_id}")
                        
                        # 返回带有AI响应的结果
                        return {
                            **response,  # 原始用户消息响应
                            "ai_message": {
                                "id": ai_messages.id,
                                "role": ai_messages.role,
                                "content": ai_messages.content,
                                "conversation_id": ai_messages.conversation_id,
                                "timestamp": ai_messages.created_at,
                                "processing_time": ai_messages.processing_time
                            }
                        }
                except asyncio.TimeoutError:
                    print(f"[{request_id}] AI响应超时")
                    # 继续异步处理AI响应
                    asyncio.create_task(process_ai_response(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message_content=db_message.content,
                        model_name=modelName,
                        use_local_model=useLocalModel,
                        use_think_mode=useThinkMode,
                        request_id=f"{request_id}-async"
                    ))
                    
                    # 释放锁
                    if message_creation_locks.get(conversation_id) == new_lock:
                        del message_creation_locks[conversation_id]
                        print(f"[{request_id}] 释放会话锁(超时): {conversation_id}")
                    
                    # 返回带有明确超时标志的结果
                    return {
                        **response,
                        "is_timeout": True,
                        "ai_message": {
                            "id": -1,  # 临时ID
                            "role": "assistant",
                            "content": "**AI响应时间过长**，消息已发送，但未能在60秒内获得响应。AI会在后台继续处理，请稍后刷新对话查看回复。",
                            "conversation_id": conversation_id,
                            "timestamp": datetime.now(timezone.utc),
                            "processing_time": 60.0,  # 预设60秒处理时间
                            "is_timeout_message": True
                        }
                    }
                except Exception as e:
                    print(f"[{request_id}] 等待AI响应时出错: {str(e)}")
                    # 异步处理AI响应
                    asyncio.create_task(process_ai_response(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message_content=db_message.content,
                        model_name=modelName,
                        use_local_model=useLocalModel,
                        use_think_mode=useThinkMode,
                        request_id=f"{request_id}-async-error"
                    ))
                    
                    # 释放锁
                    if message_creation_locks.get(conversation_id) == new_lock:
                        del message_creation_locks[conversation_id]
                        print(f"[{request_id}] 释放会话锁(错误): {conversation_id}")
                    
                    # 返回带有错误标志的结果
                    return {
                        **response,
                        "has_error": True,
                        "error": str(e),
                        "ai_message": {
                            "id": -1,
                            "role": "assistant",
                            "content": f"处理消息时出错: {str(e)}，请稍后重试。",
                            "conversation_id": conversation_id,
                            "timestamp": datetime.now(timezone.utc),
                            "processing_time": 0.0,
                            "is_error_message": True
                        }
                    }
            else:
                # 在新的隔离会话中启动AI响应任务 
                asyncio.create_task(process_ai_response(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_content=db_message.content,
                    model_name=modelName,
                    use_local_model=useLocalModel,
                    use_think_mode=useThinkMode,
                    request_id=request_id
                ))
        
        # 释放锁
        if message_creation_locks.get(conversation_id) == new_lock:
            del message_creation_locks[conversation_id]
            print(f"[{request_id}] 释放会话锁: {conversation_id}")
        
        return response
        
    except Exception as e:
        print(f"[{request_id}] 处理消息时出现错误: {str(e)}")
        # 释放锁
        if message_creation_locks.get(conversation_id) == new_lock:
            del message_creation_locks[conversation_id]
            print(f"[{request_id}] 释放会话锁(错误情况): {conversation_id}")
        raise HTTPException(
            status_code=500,
            detail=f"处理消息失败: {str(e)}"
        )

# 新增AI响应处理函数，使用单独的会话
async def process_ai_response(
    user_id: int,
    conversation_id: int,
    message_content: str,
    model_name: str,
    use_local_model: bool,
    use_think_mode: bool,
    request_id: str
):
    """在独立的会话中处理AI回复"""
    try:
        # 创建一个独立会话，不使用事务上下文管理器
        # 避免与ai_assistant.process_query内部的事务管理冲突
        session = async_session()
        
        try:
            # 确保会话以干净状态开始
            await session.rollback()
            
            # 获取对话历史作为上下文
            messages = await message_crud.get_conversation_messages(
                session,
                conversation_id=conversation_id,
                limit=100  # 最近100条消息作为上下文
            )
            
            context_data = {
                "conversation_id": conversation_id,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
            }
            
            # 增加额外上下文数据
            context_data["useLocalModel"] = use_local_model
            context_data["modelName"] = model_name
            context_data["useThinkMode"] = use_think_mode
            
            # 调用AI服务处理查询
            print(f"[{request_id}] 开始处理AI响应 (用户: {user_id}, 会话: {conversation_id})")
            await ai_assistant.process_query(
                session,
                user_id=user_id,
                query_text=message_content,
                context_data=context_data
            )
            print(f"[{request_id}] AI响应处理完成")
        except Exception as inner_error:
            # 记录详细错误信息
            print(f"[{request_id}] AI处理内部错误: {str(inner_error)}")
            # 确保回滚会话
            await session.rollback()
            raise
        finally:
            # 确保关闭会话
            await session.close()
            print(f"[{request_id}] AI响应处理会话已关闭")
    except Exception as e:
        print(f"[{request_id}] AI响应处理失败: {str(e)}")

@router.delete(
    "/conversations/{conversation_id}/messages/{message_id}",
    response_model=ResponseBase,
    status_code=status.HTTP_200_OK,
)
async def delete_message(
    conversation_id: int = Path(..., gt=0),
    message_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/ai-assistant/conversations/{conversation_id}/messages/{message_id}", method="DELETE")
) -> Any:
    """
    删除指定对话中的特定消息
    """
    # 检查对话是否存在并属于当前用户
    conversation = await conversation_crud.get_conversation_with_messages(
        db, conversation_id=conversation_id, user_id=current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问",
        )
    
    # 删除消息关联的上传文件
    await upload_service.delete_entity_files(
        db=db, 
        entity_type="ai_message", 
        entity_id=message_id
    )
    
    # 删除消息
    success = await message_crud.delete_message(
        db, message_id=message_id, conversation_id=conversation_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或已被删除",
        )
    
    return {"status": "success", "message": "消息已成功删除"}
