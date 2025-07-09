from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_conversation import AIMessage
from app.models.uploads import Upload

async def get_message_with_attachments(db: AsyncSession, message_id: int) -> Optional[Dict[str, Any]]:
    """获取消息及其附件"""
    query = select(AIMessage).where(AIMessage.id == message_id)
    result = await db.execute(query)
    message = result.scalars().first()
    
    if not message:
        return None
    
    # 使用通用的entity_type和entity_id查询附件
    query_attachments = select(Upload).where(
        Upload.entity_type == "ai_message",
        Upload.entity_id == message_id
    )
    result_attachments = await db.execute(query_attachments)
    attachments = result_attachments.scalars().all()
    
    # 处理附件数据
    attachment_data = []
    for upload in attachments:
        file_url = f"/uploads/{upload.file_path}"
        attachment_data.append({
            "filename": upload.original_filename,
            "file_path": upload.file_path,
            "file_type": upload.file_type,
            "file_size": upload.file_size,
            "file_url": file_url,
            "upload_id": upload.id
        })
    
    # 构建完整的消息对象
    message_data = {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
        "processing_time": message.processing_time,
        "use_local_model": message.use_local_model,
        "model_name": message.model_name
    }
    
    if attachment_data:
        message_data["attachments"] = attachment_data
    
    return message_data

async def get_conversation_messages(
    db: AsyncSession, conversation_id: int, skip: int = 0, limit: int = 100
) -> List[AIMessage]:
    """获取对话的消息列表"""
    query = (
        select(AIMessage)
        .filter(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def delete_message(
    db: AsyncSession, message_id: int, conversation_id: int
) -> bool:
    """删除消息"""
    query = select(AIMessage).filter(
        AIMessage.id == message_id, 
        AIMessage.conversation_id == conversation_id
    )
    result = await db.execute(query)
    message = result.scalars().first()
    
    if not message:
        return False
    
    # 删除消息的同时，关联的附件仍保留在Upload表中
    # 如果需要删除附件，应当调用upload_service.delete_entity_files
    
    await db.delete(message)
    await db.commit()
    return True 