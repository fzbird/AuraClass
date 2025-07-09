from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.models.user import User
from app.services.statistics import (
    get_summary_stats, 
    get_student_stats, 
    get_class_stats, 
    get_item_stats, 
    get_time_series_stats,
    get_student_rankings,
    get_record_trends,
    get_item_usage_frequency,
    get_class_comparisons,
    get_top_students
)

router = APIRouter()

@router.get("/summary")
async def get_statistics_summary(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/summary", method="GET")
) -> Dict[str, Any]:
    """
    获取统计概览数据
    """
    stats = await get_summary_stats(db, start_date=start_date, end_date=end_date)
    return {
        "data": stats,
        "meta": {}
    }

@router.get("/students")
async def get_statistics_by_student(
    db: AsyncSession = Depends(get_db),
    student_id: Optional[int] = Query(None, gt=0),
    class_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/students", method="GET")
) -> Dict[str, Any]:
    """
    获取学生统计数据
    """
    stats = await get_student_stats(
        db, 
        student_id=student_id,
        class_id=class_id,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": stats,
        "meta": {
            "count": len(stats)
        }
    }

@router.get("/classes")
async def get_statistics_by_class(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/classes", method="GET")
) -> Dict[str, Any]:
    """
    获取班级统计数据
    """
    stats = await get_class_stats(db, start_date=start_date, end_date=end_date)
    return {
        "data": stats,
        "meta": {
            "count": len(stats)
        }
    }

@router.get("/items")
async def get_statistics_by_item(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/items", method="GET")
) -> Dict[str, Any]:
    """
    获取量化项目统计数据
    """
    stats = await get_item_stats(
        db, 
        category=category,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": stats,
        "meta": {
            "count": len(stats)
        }
    }

@router.get("/timeline")
async def get_time_series_statistics(
    db: AsyncSession = Depends(get_db),
    interval: str = Query("day", regex="^(day|week|month)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/timeline", method="GET")
) -> Dict[str, Any]:
    """
    获取时间序列统计数据
    """
    stats = await get_time_series_stats(
        db, 
        interval=interval,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": stats,
        "meta": {
            "count": len(stats),
            "interval": interval
        }
    }

@router.get("/student/{student_id}")
async def get_student_detailed_stats(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/student/{student_id}", method="GET")
) -> Dict[str, Any]:
    """
    获取单个学生的详细统计数据
    """
    # 获取学生基本统计数据
    student_stats = await get_student_stats(
        db, 
        student_id=student_id,
        start_date=start_date, 
        end_date=end_date
    )
    
    if not student_stats:
        raise HTTPException(
            status_code=404,
            detail="找不到指定学生的统计数据"
        )
    
    # 获取学生的项目分布统计
    item_stats = await get_item_stats(
        db, 
        start_date=start_date, 
        end_date=end_date
    )
    
    # 筛选出该学生的项目数据 (实际中应该优化查询)
    student_item_stats = []
    
    return {
        "data": {
            "basic_stats": student_stats[0] if student_stats else {},
            "item_distribution": student_item_stats
        },
        "meta": {}
    }

@router.get("/student-rankings")
async def get_student_rankings_endpoint(
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, gt=0),
    item_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, gt=0, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    获取学生排名数据
    """
    rankings = await get_student_rankings(
        db, 
        class_id=class_id,
        item_id=item_id,
        start_date=start_date, 
        end_date=end_date,
        limit=limit
    )
    return {
        "data": rankings,
        "meta": {
            "count": len(rankings)
        }
    }

@router.get("/trends")
async def get_quant_trends(
    db: AsyncSession = Depends(get_db),
    interval: str = Query("day", regex="^(day|week|month)$"),
    class_id: Optional[int] = Query(None, gt=0),
    student_id: Optional[int] = Query(None, gt=0),
    item_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/trends", method="GET")
) -> Dict[str, Any]:
    """
    获取量化记录趋势数据
    """
    trends = await get_record_trends(
        db, 
        interval=interval,
        class_id=class_id,
        student_id=student_id,
        item_id=item_id,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": trends,
        "meta": {
            "count": len(trends),
            "interval": interval
        }
    }

@router.get("/item-usage")
async def get_item_usage_statistics(
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, gt=0),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(20, gt=0, le=100),
    current_user: User = require_permissions(path="/api/v1/stats/item-usage", method="GET")
) -> Dict[str, Any]:
    """
    获取量化项目使用频率
    """
    usage_data = await get_item_usage_frequency(
        db, 
        class_id=class_id,
        category=category,
        start_date=start_date, 
        end_date=end_date,
        limit=limit
    )
    return {
        "data": usage_data,
        "meta": {
            "count": len(usage_data)
        }
    }

@router.get("/class-comparisons")
async def get_class_comparison_data(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/class-comparisons", method="GET")
) -> Dict[str, Any]:
    """
    获取班级比较数据
    """
    comparison_data = await get_class_comparisons(
        db, 
        category=category,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": comparison_data,
        "meta": {
            "count": len(comparison_data)
        }
    }

@router.get("/top-students")
async def get_top_students_data(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, gt=0, le=100),
    class_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/stats/top-students", method="GET")
) -> Dict[str, Any]:
    """
    获取顶尖学生数据
    """
    students_data = await get_top_students(
        db, 
        limit=limit,
        class_id=class_id,
        start_date=start_date, 
        end_date=end_date
    )
    return {
        "data": students_data,
        "meta": {
            "count": len(students_data)
        }
    }

@router.get("/export")
async def export_statistics_data(
    db: AsyncSession = Depends(get_db),
    type: str = Query("records", regex="^(students|records|items|classes|rankings)$"),
    format: str = Query("csv", regex="^(csv|excel)$"),
    class_id: Optional[int] = Query(None, gt=0),
    student_id: Optional[int] = Query(None, gt=0),
    item_id: Optional[int] = Query(None, gt=0),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(1000, gt=0, le=5000),
    current_user: User = require_permissions(path="/api/v1/stats/export", method="GET")
) -> Any:
    """
    导出统计数据
    """
    filters = {
        "class_id": class_id,
        "student_id": student_id,
        "item_id": item_id,
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    
    return await export_stats(db, type=type, format=format, filters=filters)
