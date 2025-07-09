from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.models.user import User
from app.services.export import (
    export_student_stats_csv,
    export_class_stats_csv,
    export_item_stats_csv,
    export_stats
)

router = APIRouter()

@router.get("/students/csv")
async def export_students_statistics_csv(
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/exports/students/csv", method="GET")
) -> Any:
    """
    导出学生统计数据为CSV
    """
    return await export_student_stats_csv(
        db, 
        class_id=class_id,
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/classes/csv")
async def export_classes_statistics_csv(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/exports/classes/csv", method="GET")
) -> Any:
    """
    导出班级统计数据为CSV
    """
    return await export_class_stats_csv(
        db,
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/items/csv")
async def export_items_statistics_csv(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/exports/items/csv", method="GET")
) -> Any:
    """
    导出量化项目统计数据为CSV
    """
    return await export_item_stats_csv(
        db,
        category=category,
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/statistics")
async def export_statistics(
    db: AsyncSession = Depends(get_db),
    type: str = Query("records", regex="^(students|records|items|classes)$"),
    format: str = Query("excel", regex="^(csv|excel)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    class_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    item_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = require_permissions(path="/api/v1/exports/statistics", method="GET")
) -> Any:
    """
    导出统计数据为文件
    
    支持的类型:
    - students: 学生统计数据
    - records: 量化记录数据
    - items: 量化项目统计数据
    - classes: 班级统计数据
    
    支持的格式:
    - csv: CSV格式
    - excel: Excel格式
    """
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "class_id": class_id,
        "student_id": student_id,
        "item_id": item_id,
        "category": category
    }
    
    # 过滤掉None值
    filters = {k: v for k, v in filters.items() if v is not None}
    
    return await export_stats(db, type=type, format=format, filters=filters)
