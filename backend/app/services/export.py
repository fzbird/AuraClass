from typing import List, Dict, Any, Optional
from datetime import date, datetime
import csv
import json
import os
import tempfile
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.statistics import (
    get_student_stats,
    get_class_stats,
    get_item_stats,
    get_time_series_stats,
    get_student_rankings
)
from app.crud.quant_record import quant_record_crud

async def export_student_stats_csv(
    db, start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    class_id: Optional[int] = None
) -> FileResponse:
    """导出学生统计数据为CSV"""
    stats = await get_student_stats(db, class_id=class_id, start_date=start_date, end_date=end_date)
    
    if not stats:
        raise HTTPException(status_code=404, detail="未找到符合条件的数据")
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = Path(temp_dir) / f"student_stats_{timestamp}.csv"
    
    # 写入CSV
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'student_id', 'student_id_no', 'full_name', 
            'class_name', 'record_count', 'total_score', 'avg_score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat)
    
    # 返回文件
    return FileResponse(
        path=file_path,
        filename=f"student_stats_{timestamp}.csv",
        media_type="text/csv"
    )

async def export_class_stats_csv(
    db, start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> FileResponse:
    """导出班级统计数据为CSV"""
    stats = await get_class_stats(db, start_date=start_date, end_date=end_date)
    
    if not stats:
        raise HTTPException(status_code=404, detail="未找到符合条件的数据")
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = Path(temp_dir) / f"class_stats_{timestamp}.csv"
    
    # 写入CSV
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'class_id', 'name', 'grade', 'student_count', 
            'record_count', 'total_score', 'avg_score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat)
    
    # 返回文件
    return FileResponse(
        path=file_path,
        filename=f"class_stats_{timestamp}.csv",
        media_type="text/csv"
    )

async def export_item_stats_csv(
    db, category: Optional[str] = None,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> FileResponse:
    """导出量化项目统计数据为CSV"""
    stats = await get_item_stats(db, category=category, start_date=start_date, end_date=end_date)
    
    if not stats:
        raise HTTPException(status_code=404, detail="未找到符合条件的数据")
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = Path(temp_dir) / f"item_stats_{timestamp}.csv"
    
    # 写入CSV
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'item_id', 'name', 'category', 'record_count', 
            'student_count', 'total_score', 'avg_score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat)
    
    # 返回文件
    return FileResponse(
        path=file_path,
        filename=f"item_stats_{timestamp}.csv",
        media_type="text/csv"
    )

async def export_stats(
    db,
    type: str = "records",  # students, records, items, classes
    format: str = "csv",  # csv, excel
    filters: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> FileResponse:
    """
    通用统计数据导出函数
    
    Args:
        db: 数据库会话
        type: 导出数据类型，可选值: students, records, items, classes
        format: 导出格式，可选值: csv, excel
        filters: 过滤条件，支持 class_id, student_id, item_id, category, start_date, end_date
        headers: 表头映射，默认根据type类型自动生成
    
    Returns:
        FileResponse 对象
    """
    from app.services.file_service import FileService
    
    if not filters:
        filters = {}
    
    # 根据类型获取数据
    data = []
    if type == "students":
        data = await get_student_stats(
            db,
            class_id=filters.get("class_id"),
            student_id=filters.get("student_id"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date")
        )
        # 默认表头
        if not headers:
            headers = {
                "student_id": "学生ID",
                "student_id_no": "学号",
                "full_name": "姓名",
                "class_name": "班级",
                "record_count": "记录数量",
                "total_score": "总分",
                "avg_score": "平均分"
            }
    elif type == "classes":
        data = await get_class_stats(
            db,
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date")
        )
        # 默认表头
        if not headers:
            headers = {
                "class_id": "班级ID",
                "name": "班级名称",
                "grade": "年级",
                "student_count": "学生数量",
                "record_count": "记录数量",
                "total_score": "总分",
                "avg_score": "平均分"
            }
    elif type == "items":
        data = await get_item_stats(
            db,
            category=filters.get("category"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date")
        )
        # 默认表头
        if not headers:
            headers = {
                "item_id": "项目ID",
                "name": "项目名称",
                "category": "类别",
                "record_count": "使用次数",
                "student_count": "学生数量",
                "total_score": "总分数",
                "avg_score": "平均分数"
            }
    elif type == "rankings":
        data = await get_student_rankings(
            db,
            class_id=filters.get("class_id"),
            item_id=filters.get("item_id"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
            limit=filters.get("limit", 50)
        )
        # 默认表头
        if not headers:
            headers = {
                "rank": "排名",
                "student_id": "学生ID",
                "student_id_no": "学号",
                "full_name": "姓名",
                "class_name": "班级",
                "record_count": "记录数量",
                "total_score": "总分",
                "avg_score": "平均分"
            }
    else:  # default to records
        records = await quant_record_crud.get_multi_with_details(
            db,
            skip=0,
            limit=1000,
            student_id=filters.get("student_id"),
            item_id=filters.get("item_id"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date")
        )
        
        for record_tuple in records:
            # 解构元组: (QuantRecord, Student, QuantItem, User, Classes)
            record, student, item, recorder, class_obj = record_tuple
            
            # 安全获取班级名称
            class_name = class_obj.name if class_obj else f"班级ID: {student.class_id}"
            
            data.append({
                "record_id": record.id,
                "student_name": student.full_name,
                "student_id_no": student.student_id_no,
                "class_name": class_name,
                "item_name": item.name,
                "score": float(record.score),
                "reason": record.reason,
                "record_date": record.record_date.isoformat() if record.record_date else "",
                "recorder_name": recorder.full_name if recorder else ""
            })
        
        # 默认表头
        if not headers:
            headers = {
                "record_id": "记录ID",
                "student_name": "学生姓名",
                "student_id_no": "学号",
                "class_name": "班级",
                "item_name": "量化项目",
                "score": "分数",
                "reason": "原因",
                "record_date": "记录日期",
                "recorder_name": "录入人"
            }
    
    if not data:
        raise HTTPException(status_code=404, detail="未找到符合条件的数据")
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_prefix = f"{type}_stats_{timestamp}"
    
    # 导出数据
    return FileService.export_data(data, headers, filename_prefix, format)

async def export_student_rankings(
    db,
    class_id: Optional[int] = None,
    item_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50,
    format: str = "csv"
) -> FileResponse:
    """
    导出学生排名数据
    
    Args:
        db: 数据库会话
        class_id: 班级ID
        item_id: 项目ID
        start_date: 开始日期
        end_date: 结束日期
        limit: 限制数量
        format: 导出格式，可选值: csv, excel
        
    Returns:
        FileResponse 对象
    """
    filters = {
        "class_id": class_id,
        "item_id": item_id,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    
    return await export_stats(db, type="rankings", format=format, filters=filters)

async def export_chart_image(
    chart_type: str,
    chart_options: Dict[str, Any]
) -> Dict[str, str]:
    """
    导出图表为图片
    
    Args:
        chart_type: 图表类型
        chart_options: 图表选项
    
    Returns:
        包含图片URL的字典
    """
    # 这里应该集成图表生成库，如 matplotlib 或通过 API 调用在线服务
    # 由于这需要额外依赖，这里只返回mock数据
    
    # 实际实现时应该:
    # 1. 使用 matplotlib 或其他库根据 chart_options 生成图表
    # 2. 保存图表为图片
    # 3. 返回图片URL或将图片上传到静态文件服务器
    
    return {
        "imageUrl": f"/static/images/charts/chart_{chart_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    }
