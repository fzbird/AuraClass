from typing import Any, Dict, List, Optional, Union
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.uploads import Upload
from app.schemas.uploads import UploadCreate, UploadUpdate


async def create(db: AsyncSession, *, obj_in: UploadCreate) -> Upload:
    """创建文件上传记录"""
    db_obj = Upload(
        filename=obj_in.filename,
        original_filename=obj_in.original_filename,
        file_path=obj_in.file_path,
        file_type=obj_in.file_type,
        file_size=obj_in.file_size,
        module=obj_in.module,
        entity_type=obj_in.entity_type,
        entity_id=obj_in.entity_id,
        uploader_id=obj_in.uploader_id,
        is_public=obj_in.is_public
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get(db: AsyncSession, id: int) -> Optional[Upload]:
    """获取单个文件上传记录"""
    result = await db.execute(select(Upload).filter(Upload.id == id))
    return result.scalars().first()


async def get_multi(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[Upload]:
    """获取多个文件上传记录"""
    result = await db.execute(select(Upload).offset(skip).limit(limit))
    return result.scalars().all()


async def get_by_entity(
    db: AsyncSession, *, entity_type: str, entity_id: int
) -> List[Upload]:
    """根据实体类型和ID获取文件上传记录"""
    result = await db.execute(
        select(Upload)
        .filter(Upload.entity_type == entity_type, Upload.entity_id == entity_id)
    )
    return result.scalars().all()


async def get_by_module(
    db: AsyncSession, *, module: str, skip: int = 0, limit: int = 100
) -> List[Upload]:
    """根据模块获取文件上传记录"""
    result = await db.execute(
        select(Upload)
        .filter(Upload.module == module)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_by_uploader(
    db: AsyncSession, *, uploader_id: int, skip: int = 0, limit: int = 100
) -> List[Upload]:
    """根据上传者ID获取文件上传记录"""
    result = await db.execute(
        select(Upload)
        .filter(Upload.uploader_id == uploader_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def count(
    db: AsyncSession, *, module: Optional[str] = None, uploader_id: Optional[int] = None
) -> int:
    """获取文件上传记录数量"""
    stmt = select(func.count(Upload.id))
    if module:
        stmt = stmt.filter(Upload.module == module)
    if uploader_id:
        stmt = stmt.filter(Upload.uploader_id == uploader_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def update(
    db: AsyncSession, *, db_obj: Upload, obj_in: Union[UploadUpdate, Dict[str, Any]]
) -> Upload:
    """更新文件上传记录"""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        if update_data[field] is not None:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, *, id: int) -> Optional[Upload]:
    """删除文件上传记录"""
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj


async def remove_by_entity(
    db: AsyncSession, *, entity_type: str, entity_id: int
) -> int:
    """根据实体类型和ID删除文件上传记录"""
    result = await db.execute(
        select(Upload)
        .filter(Upload.entity_type == entity_type, Upload.entity_id == entity_id)
    )
    objects = result.scalars().all()
    
    for obj in objects:
        await db.delete(obj)
    
    await db.commit()
    return len(objects) 