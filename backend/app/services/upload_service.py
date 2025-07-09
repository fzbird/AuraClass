import os
import uuid
from datetime import datetime
from typing import List, Optional, Union
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.uploads import Upload
from app.schemas.uploads import UploadCreate, Upload as UploadSchema
from app.crud import uploads as crud_uploads


class UploadService:
    """文件上传服务，提供通用的文件上传、获取和删除功能"""
    
    async def save_upload(
        self,
        *,
        db: AsyncSession,
        file: UploadFile,
        module: str,
        uploader_id: int,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        is_public: int = 0
    ) -> UploadSchema:
        """保存上传文件并创建数据库记录"""
        # 验证文件类型
        file_type = file.content_type or "application/octet-stream"
        if file_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_type}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 验证文件大小
        file_size = len(file_content)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({file_size / 1024 / 1024:.1f}MB > {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB)"
            )
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 构建保存路径
        relative_path = f"{module}/{uploader_id}"
        if entity_type and entity_id:
            relative_path = f"{relative_path}/{entity_type}_{entity_id}"
            
        # 确保目录存在
        upload_dir = Path(settings.UPLOADS_DIR) / relative_path
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = upload_dir / unique_filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 生成相对路径和URL
        relative_file_path = f"{relative_path}/{unique_filename}"
        file_url = f"/uploads/{relative_file_path}"
        
        # 创建数据库记录
        upload_in = UploadCreate(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=relative_file_path,
            file_type=file_type,
            file_size=file_size,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            uploader_id=uploader_id,
            is_public=is_public
        )
        
        db_upload = await crud_uploads.create(db, obj_in=upload_in)
        
        # 返回包含URL的完整模型
        return UploadSchema(
            **db_upload.__dict__,
            file_url=file_url
        )
    
    async def save_multiple_uploads(
        self,
        *,
        db: AsyncSession,
        files: List[UploadFile],
        module: str,
        uploader_id: int,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        is_public: int = 0
    ) -> List[UploadSchema]:
        """保存多个上传文件并创建数据库记录"""
        # 验证文件数量
        if len(files) > settings.MAX_FILES_PER_REQUEST:
            raise HTTPException(
                status_code=400,
                detail=f"最多允许上传 {settings.MAX_FILES_PER_REQUEST} 个文件"
            )
        
        results = []
        for file in files:
            if file.filename:  # 跳过空文件
                upload = await self.save_upload(
                    db=db,
                    file=file,
                    module=module,
                    uploader_id=uploader_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    is_public=is_public
                )
                results.append(upload)
        
        return results
    
    async def get_file_url(self, upload: Upload) -> str:
        """获取文件的完整URL"""
        return f"/uploads/{upload.file_path}"
    
    async def delete_file(self, *, db: AsyncSession, upload_id: int) -> bool:
        """删除文件及其数据库记录"""
        upload = await crud_uploads.get(db, upload_id)
        if not upload:
            return False
        
        # 删除物理文件
        file_path = Path(settings.UPLOADS_DIR) / upload.file_path
        if file_path.exists():
            try:
                file_path.unlink()  # 删除文件
                
                # 尝试删除空目录
                parent_dir = file_path.parent
                if parent_dir.exists() and not any(parent_dir.iterdir()):
                    parent_dir.rmdir()
            except Exception as e:
                # 记录错误但继续删除数据库记录
                print(f"删除文件时出错: {str(e)}")
        
        # 删除数据库记录
        await crud_uploads.remove(db, id=upload_id)
        return True
    
    async def delete_entity_files(
        self, *, db: AsyncSession, entity_type: str, entity_id: int
    ) -> int:
        """删除与实体相关的所有文件及其数据库记录"""
        uploads = await crud_uploads.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id
        )
        
        count = 0
        for upload in uploads:
            # 删除物理文件
            file_path = Path(settings.UPLOADS_DIR) / upload.file_path
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass  # 忽略错误，继续处理其他文件
            
            count += 1
        
        # 批量删除数据库记录
        await crud_uploads.remove_by_entity(
            db, entity_type=entity_type, entity_id=entity_id
        )
        
        return count


# 创建服务实例
upload_service = UploadService() 