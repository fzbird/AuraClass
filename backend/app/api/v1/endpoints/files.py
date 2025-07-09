from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.models.user import User
from app.services.file_service import FileService

router = APIRouter()

@router.post("/students/import")
async def import_students(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/files/students/import", method="POST")
) -> Any:
    """
    导入学生数据（支持CSV和Excel格式）
    """
    success_count, errors = await FileService.import_students(
        db,
        file=file,
        current_user_id=current_user.id
    )
    
    return {
        "message": f"成功导入{success_count}条学生数据",
        "success_count": success_count,
        "errors": errors
    }

@router.post("/quant-records/import")
async def import_quant_records(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/files/quant-records/import", method="POST")
) -> Any:
    """
    导入量化记录数据（支持CSV和Excel格式）
    """
    success_count, errors = await FileService.import_quant_records(
        db,
        file=file,
        current_user_id=current_user.id
    )
    
    return {
        "message": f"成功导入{success_count}条量化记录",
        "success_count": success_count,
        "errors": errors
    }

@router.get("/templates/student-import")
async def get_student_import_template(
    format: str = Query(..., regex="^(csv|excel)$"),
    current_user: User = require_permissions(path="/api/v1/files/templates/student-import", method="GET")
) -> Any:
    """
    获取学生导入模板
    """
    # 定义表头，注明必填字段
    headers = {
        "student_id_no": "学号（必填）",
        "full_name": "姓名（必填）",
        "class_id": "班级ID（必填）",
        "gender": "性别（选填，填写：男/女）",
        "birth_date": "出生日期（选填，格式：YYYY-MM-DD）",
        "contact_info": "联系方式（选填）"
    }
    
    # 创建多行示例数据
    sample_data = [
        {
            # 注释行将作为第一行数据
            "student_id_no": "# 填写学号，必须唯一，例如：S20230001",
            "full_name": "# 填写学生姓名",
            "class_id": "# 填写班级ID，必须是系统中已存在的班级ID",
            "gender": "# 填写性别：男/女，可以为空",
            "birth_date": "# 填写出生日期，格式：YYYY-MM-DD，可以为空",
            "contact_info": "# 填写联系方式，可以为空"
        },
        {
            # 完整示例
            "student_id_no": "S20230001",
            "full_name": "张三",
            "class_id": "1",
            "gender": "男",
            "birth_date": "2000-01-01",
            "contact_info": "13800138000"
        },
        {
            # 另一个示例，只有必填字段
            "student_id_no": "S20230002",
            "full_name": "李四",
            "class_id": "2",
            "gender": "",
            "birth_date": "",
            "contact_info": ""
        },
        {
            # 女生示例
            "student_id_no": "S20230003",
            "full_name": "王五",
            "class_id": "1",
            "gender": "女",
            "birth_date": "2000-05-05",
            "contact_info": "父亲：13900139000"
        }
    ]
    
    return FileService.export_data(
        data=sample_data,
        headers=headers,
        filename_prefix="学生信息导入模板",  # 使用中文文件名
        format=format
    )

@router.get("/templates/quant-record-import")
async def get_quant_record_import_template(
    format: str = Query(..., regex="^(csv|excel)$"),
    current_user: User = require_permissions(path="/api/v1/files/templates/quant-record-import", method="GET")
) -> Any:
    """
    获取量化记录导入模板
    """
    # 定义表头，注明必填字段
    headers = {
        "student_id": "学生ID（必填）",
        "item_id": "量化项目ID（必填）",
        "score": "分数（必填，范围0-100）",
        "reason": "原因（选填）",
        "record_date": "记录日期（必填，格式：YYYY-MM-DD）"
    }
    
    # 创建多行示例数据
    sample_data = [
        {
            # 注释行将作为第一行数据
            "student_id": "# 填写学生ID，必须是系统中已存在的学生ID",
            "item_id": "# 填写量化项目ID，必须是系统中已存在的项目ID",
            "score": "# 填写分数，范围0-100，可以包含小数",
            "reason": "# 填写评分原因，可以为空",
            "record_date": "# 填写记录日期，格式为YYYY-MM-DD"
        },
        {
            # 第一个示例 - 优秀表现
            "student_id": "1",
            "item_id": "1",
            "score": "85.5",
            "reason": "表现优秀，课堂积极发言",
            "record_date": "2023-05-01"
        },
        {
            # 第二个示例 - 作业不及时
            "student_id": "2",
            "item_id": "3",
            "score": "65",
            "reason": "作业完成不及时",
            "record_date": "2023-05-02"
        },
        {
            # 第三个示例 - 满分和空理由
            "student_id": "3",
            "item_id": "2",
            "score": "100",
            "reason": "",  # 原因字段可以为空
            "record_date": "2023-05-03"
        }
    ]
    
    return FileService.export_data(
        data=sample_data,
        headers=headers,
        filename_prefix="量化记录导入模板",  # 使用中文文件名
        format=format
    )
