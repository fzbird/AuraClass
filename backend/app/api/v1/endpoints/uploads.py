from typing import Any, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Path, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_permissions
from app.services.upload_service import upload_service
from app.schemas.uploads import Upload, UploadList
from app.crud import uploads as crud_uploads

router = APIRouter()


@router.post("", response_model=Upload)
async def upload_file(
    *,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    module: str = Form(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[int] = Form(None),
    is_public: int = Form(0),
    current_user: User = require_permissions(path="/api/v1/uploads", method="POST")
) -> Any:
    """
    上传单个文件
    """
    return await upload_service.save_upload(
        db=db,
        file=file,
        module=module,
        uploader_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        is_public=is_public
    )


@router.post("/multiple", response_model=List[Upload])
async def upload_multiple_files(
    *,
    db: AsyncSession = Depends(get_db),
    files: List[UploadFile] = File(...),
    module: str = Form(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[int] = Form(None),
    is_public: int = Form(0),
    current_user: User = require_permissions(path="/api/v1/uploads/multiple", method="POST")
) -> Any:
    """
    上传多个文件
    """
    return await upload_service.save_multiple_uploads(
        db=db,
        files=files,
        module=module,
        uploader_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        is_public=is_public
    )


@router.get("", response_model=UploadList)
async def list_uploads(
    *,
    db: AsyncSession = Depends(get_db),
    module: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = require_permissions(path="/api/v1/uploads", method="GET")
) -> Any:
    """
    获取上传文件列表
    """
    # 构建查询条件
    filters = {}
    if module:
        filters["module"] = module
    
    # 根据不同条件查询文件
    if entity_type and entity_id:
        uploads = await crud_uploads.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id
        )
        total = len(uploads)
    elif module:
        uploads = await crud_uploads.get_by_module(
            db, module=module, skip=skip, limit=limit
        )
        total = await crud_uploads.count(db, module=module)
    else:
        # 默认只显示当前用户上传的文件
        uploads = await crud_uploads.get_by_uploader(
            db, uploader_id=current_user.id, skip=skip, limit=limit
        )
        total = await crud_uploads.count(db, uploader_id=current_user.id)
    
    # 转换为带URL的模型
    results = []
    for upload in uploads:
        file_url = await upload_service.get_file_url(upload)
        results.append(Upload(
            **upload.__dict__,
            file_url=file_url
        ))
    
    return UploadList(
        uploads=results,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )


@router.get("/{id}", response_model=Upload)
async def get_upload(
    *,
    db: AsyncSession = Depends(get_db),
    id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/uploads/{id}", method="GET")
) -> Any:
    """
    获取单个上传文件信息
    """
    upload = await crud_uploads.get(db, id)
    if not upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查权限：如果不是公开文件，只能被上传者查看
    if upload.is_public != 1 and upload.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此文件")
    
    file_url = await upload_service.get_file_url(upload)
    return Upload(
        **upload.__dict__,
        file_url=file_url
    )


@router.delete("/{id}")
async def delete_upload(
    *,
    db: AsyncSession = Depends(get_db),
    id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/uploads/{id}", method="DELETE")
) -> Any:
    """
    删除上传文件
    """
    upload = await crud_uploads.get(db, id)
    if not upload:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查权限：只能删除自己上传的文件
    if upload.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此文件")
    
    success = await upload_service.delete_file(db=db, upload_id=id)
    return {"success": success} 