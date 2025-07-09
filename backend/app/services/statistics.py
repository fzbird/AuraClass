from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_, case

from app.models.quant_record import QuantRecord
from app.models.student import Student
from app.models.quant_item import QuantItem
from app.models.classes import Classes

async def get_summary_stats(
    db: AsyncSession, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """获取总体统计概览"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 获取记录总数
    query = select(func.count()).select_from(QuantRecord).where(and_(*conditions))
    result = await db.execute(query)
    total_records = result.scalar_one()
    
    # 获取参与学生数
    query = select(func.count(Student.id.distinct())).select_from(QuantRecord).join(
        Student, QuantRecord.student_id == Student.id
    ).where(and_(*conditions))
    result = await db.execute(query)
    students_with_records = result.scalar_one()
    
    # 获取总学生数
    query = select(func.count()).select_from(Student)
    result = await db.execute(query)
    total_students = result.scalar_one()
    
    # 获取量化项目数
    query = select(func.count(QuantItem.id.distinct())).select_from(QuantRecord).join(
        QuantItem, QuantRecord.item_id == QuantItem.id
    ).where(and_(*conditions))
    result = await db.execute(query)
    total_items = result.scalar_one()
    
    # 获取总积分
    query = select(func.sum(QuantRecord.score)).select_from(QuantRecord).where(and_(*conditions))
    result = await db.execute(query)
    total_score = result.scalar_one() or 0
    
    # 获取平均分
    query = select(func.avg(QuantRecord.score)).select_from(QuantRecord).where(and_(*conditions))
    result = await db.execute(query)
    average_score = result.scalar_one() or 0
    
    # 获取月度记录数
    monthly_conditions = conditions.copy()
    month_start = date.today().replace(day=1)
    monthly_conditions.append(QuantRecord.record_date >= month_start)
    
    query = select(func.count()).select_from(QuantRecord).where(and_(*monthly_conditions))
    result = await db.execute(query)
    monthly_records = result.scalar_one()
    
    # 计算正负记录比例
    query = select(
        func.sum(func.if_(QuantRecord.score > 0, 1, 0)).label("positive_count"),
        func.sum(func.if_(QuantRecord.score < 0, 1, 0)).label("negative_count"),
        func.sum(func.if_(QuantRecord.score == 0, 1, 0)).label("neutral_count")
    ).select_from(QuantRecord).where(and_(*conditions))
    result = await db.execute(query)
    row = result.one()
    
    positive_count = row.positive_count or 0
    negative_count = row.negative_count or 0
    neutral_count = row.neutral_count or 0
    
    total_count = positive_count + negative_count + neutral_count
    
    positive_percentage = (positive_count / total_count) if total_count > 0 else 0
    negative_percentage = (negative_count / total_count) if total_count > 0 else 0
    neutral_percentage = (neutral_count / total_count) if total_count > 0 else 0
    
    # 获取类别统计
    query = (
        select(
            QuantItem.category,
            func.count(QuantRecord.id).label("count"),
            func.sum(QuantRecord.score).label("score"),
            func.avg(QuantRecord.score).label("average")
        )
        .select_from(QuantRecord)
        .join(QuantItem, QuantRecord.item_id == QuantItem.id)
        .where(and_(*conditions))
        .group_by(QuantItem.category)
    )
    result = await db.execute(query)
    
    categories = []
    for row in result:
        if row.category: # 排除空类别
            categories.append({
                "category": row.category,
                "count": row.count,
                "score": float(row.score) if row.score else 0,
                "average": float(row.average) if row.average else 0
            })
    
    # 获取项目分布统计
    item_distribution = await get_item_usage_frequency(
        db, 
        start_date=start_date, 
        end_date=end_date,
        limit=10
    )
    
    # 计算每个项目的百分比
    if item_distribution and total_records > 0:
        total_counts = sum(item["count"] for item in item_distribution)
        for item in item_distribution:
            item["percentage"] = item["count"] / total_counts
    
    return {
        "total_records": total_records,
        "total_students": total_students,
        "total_items": total_items,
        "total_score": float(total_score),
        "average_score": float(average_score),
        "monthly_records": monthly_records,
        "students_with_records": students_with_records,
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage,
        "neutral_percentage": neutral_percentage,
        "categories": categories,
        "itemDistribution": item_distribution
    }

async def get_student_stats(
    db: AsyncSession, 
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """按学生统计"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建基础条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 添加学生或班级过滤条件
    if student_id:
        conditions.append(QuantRecord.student_id == student_id)
    elif class_id:
        conditions.append(Student.class_id == class_id)
    
    # 查询学生统计数据
    query = (
        select(
            Student.id,
            Student.student_id_no,
            Student.full_name,
            Classes.name.label("class_name"),
            func.count(QuantRecord.id).label("record_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        )
        .select_from(QuantRecord)
        .join(Student, QuantRecord.student_id == Student.id)
        .join(Classes, Student.class_id == Classes.id)
        .where(and_(*conditions))
        .group_by(Student.id, Student.student_id_no, Student.full_name, Classes.name)
        .order_by(desc("total_score"))
    )
    
    result = await db.execute(query)
    students_data = []
    
    for row in result:
        students_data.append({
            "student_id": row.id,
            "student_id_no": row.student_id_no,
            "full_name": row.full_name,
            "class_name": row.class_name,
            "record_count": row.record_count,
            "total_score": float(row.total_score) if row.total_score else 0,
            "avg_score": float(row.avg_score) if row.avg_score else 0
        })
    
    return students_data

async def get_class_stats(
    db: AsyncSession,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """按班级统计"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 查询班级统计数据
    query = (
        select(
            Classes.id,
            Classes.name,
            Classes.grade,
            func.count(Student.id.distinct()).label("student_count"),
            func.count(QuantRecord.id).label("record_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        )
        .select_from(QuantRecord)
        .join(Student, QuantRecord.student_id == Student.id)
        .join(Classes, Student.class_id == Classes.id)
        .where(and_(*conditions))
        .group_by(Classes.id, Classes.name, Classes.grade)
        .order_by(desc("total_score"))
    )
    
    result = await db.execute(query)
    classes_data = []
    
    for row in result:
        classes_data.append({
            "class_id": row.id,
            "name": row.name,
            "grade": row.grade,
            "student_count": row.student_count,
            "record_count": row.record_count,
            "total_score": float(row.total_score) if row.total_score else 0,
            "avg_score": float(row.avg_score) if row.avg_score else 0
        })
    
    return classes_data

async def get_item_stats(
    db: AsyncSession,
    category: Optional[str] = None,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """按量化项目统计"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建基础条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 添加类别过滤条件
    if category:
        conditions.append(QuantItem.category == category)
    
    # 查询项目统计数据
    query = (
        select(
            QuantItem.id,
            QuantItem.name,
            QuantItem.category,
            func.count(QuantRecord.id).label("record_count"),
            func.count(Student.id.distinct()).label("student_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        )
        .select_from(QuantRecord)
        .join(QuantItem, QuantRecord.item_id == QuantItem.id)
        .join(Student, QuantRecord.student_id == Student.id)
        .where(and_(*conditions))
        .group_by(QuantItem.id, QuantItem.name, QuantItem.category)
        .order_by(desc("record_count"))
    )
    
    result = await db.execute(query)
    items_data = []
    
    for row in result:
        items_data.append({
            "item_id": row.id,
            "name": row.name,
            "category": row.category,
            "record_count": row.record_count,
            "student_count": row.student_count,
            "total_score": float(row.total_score) if row.total_score else 0,
            "avg_score": float(row.avg_score) if row.avg_score else 0
        })
    
    return items_data

async def get_time_series_stats(
    db: AsyncSession,
    interval: str = "day",  # day, week, month
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """时间序列统计"""
    # 设置默认日期范围
    if not start_date:
        if interval == "day":
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        elif interval == "week":
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
        else:  # month
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
    elif not end_date:
        end_date = date.today()
    
    # 创建条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 根据时间间隔选择分组函数
    if interval == "day":
        # 日期格式化 - 兼容多种数据库
        date_trunc = func.date(QuantRecord.record_date)
    elif interval == "week":
        # MySQL 周格式化
        # 使用第一个参数1表示周从周一开始，这与大多数地区的惯例一致
        year_part = func.date_format(QuantRecord.record_date, '%Y')
        week_part = func.lpad(func.week(QuantRecord.record_date, 1), 2, '0')  # 补零确保两位数
        
        # 连接成 "YYYY-WXX" 格式，如 "2023-W01"
        date_trunc = func.concat(year_part, '-W', week_part)
    else:  # month
        # MySQL 月份格式化 - "YYYY-MM"
        date_trunc = func.date_format(QuantRecord.record_date, '%Y-%m')
    
    # 查询时间序列数据
    query = (
        select(
            date_trunc.label("time_period"),
            func.count(QuantRecord.id).label("record_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        )
        .select_from(QuantRecord)
        .where(and_(*conditions))
        .group_by("time_period")
    )
    
    result = await db.execute(query)
    time_series_data = []
    
    for row in result:
        time_series_data.append({
            "time_period": row.time_period,
            "record_count": row.record_count,
            "total_score": float(row.total_score) if row.total_score else 0,
            "avg_score": float(row.avg_score) if row.avg_score else 0
        })
    
    return time_series_data

async def get_student_rankings(
    db: AsyncSession,
    class_id: Optional[int] = None,
    item_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """获取学生排名数据"""
    # 创建基础条件 - 默认情况下不应用日期过滤
    base_conditions = []
    
    # 仅当明确提供日期参数时才添加日期过滤
    date_conditions = []
    if start_date:
        date_conditions.append(QuantRecord.record_date >= start_date)
    if end_date:
        date_conditions.append(QuantRecord.record_date <= end_date)
    
    # 记录日期筛选情况用于调试
    print(f"日期筛选: {date_conditions}")
    
    # 添加其他过滤条件
    if item_id:
        base_conditions.append(QuantRecord.item_id == item_id)

    # 获取所有符合条件的学生记录
    students_query = select(
        Student.id, 
        Student.student_id_no,
        Student.full_name,
        Classes.id.label("class_id"),
        Classes.name.label("class_name")
    ).join(
        Classes, Student.class_id == Classes.id
    )
    
    if class_id:
        students_query = students_query.where(Student.class_id == class_id)
    
    students_result = await db.execute(students_query)
    students = students_result.all()
    
    rankings = []
    
    # 为每个学生计算统计数据
    for student in students:
        # 构建该学生的基础查询条件
        query_conditions = [QuantRecord.student_id == student.id] + base_conditions.copy()
        
        # 添加日期过滤条件(如果有)
        if date_conditions:
            query_conditions.extend(date_conditions)
        
        # 查询该学生的记录总数
        count_query = select(func.count()).select_from(QuantRecord).where(and_(*query_conditions))
        count_result = await db.execute(count_query)
        record_count = count_result.scalar() or 0
        
        if record_count == 0:
            continue  # 跳过没有记录的学生
        
        # 查询该学生的总分和平均分
        score_query = select(
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        ).select_from(QuantRecord).where(and_(*query_conditions))
        
        score_result = await db.execute(score_query)
        score_row = score_result.one()
        total_score = float(score_row.total_score) if score_row.total_score is not None else 0
        avg_score = float(score_row.avg_score) if score_row.avg_score is not None else 0
        
        # 查询正分总和和正分记录数
        positive_conditions = query_conditions.copy()
        positive_conditions.append(QuantRecord.score > 0)
        positive_query = select(
            func.sum(QuantRecord.score).label("positive_score"),
            func.count().label("positive_count")
        ).select_from(QuantRecord).where(and_(*positive_conditions))
        
        positive_result = await db.execute(positive_query)
        positive_row = positive_result.one()
        positive_score = float(positive_row.positive_score) if positive_row.positive_score is not None else 0
        positive_count = positive_row.positive_count or 0
        
        # 查询负分总和和负分记录数
        negative_conditions = query_conditions.copy()
        negative_conditions.append(QuantRecord.score < 0)
        negative_query = select(
            func.sum(QuantRecord.score).label("negative_score"),
            func.count().label("negative_count")
        ).select_from(QuantRecord).where(and_(*negative_conditions))
        
        negative_result = await db.execute(negative_query)
        negative_row = negative_result.one()
        negative_score = float(negative_row.negative_score) if negative_row.negative_score is not None else 0
        negative_count = negative_row.negative_count or 0
        
        # 添加到排名列表
        rankings.append({
            "student_id": student.id,
            "student_id_no": student.student_id_no,
            "full_name": student.full_name,
            "class_name": student.class_name,
            "class_id": student.class_id,
            "record_count": record_count,
            "total_score": total_score,
            "avg_score": avg_score,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "positive": positive_count,
            "negative": negative_count,
            "rank": 0  # 临时排名，将在排序后更新
        })
    
    # 按总分排序
    rankings.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 更新排名
    for idx, ranking in enumerate(rankings[:limit], 1):
        ranking["rank"] = idx
    
    return rankings[:limit]

async def get_record_trends(
    db: AsyncSession,
    interval: str = "day",  # day, week, month
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    item_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """获取量化记录趋势数据"""
    # 设置默认日期范围
    if not start_date:
        if interval == "day":
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        elif interval == "week":
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
        else:  # month
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
    elif not end_date:
        end_date = date.today()
    
    # 创建基础条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 添加过滤条件
    if class_id:
        conditions.append(Student.class_id == class_id)
    if student_id:
        conditions.append(QuantRecord.student_id == student_id)
    if item_id:
        conditions.append(QuantRecord.item_id == item_id)
    
    # 根据时间间隔选择分组函数
    if interval == "day":
        # 日期格式化 - 兼容多种数据库
        date_trunc = func.date(QuantRecord.record_date)
    elif interval == "week":
        # MySQL 周格式化
        # 使用第一个参数1表示周从周一开始，这与大多数地区的惯例一致
        year_part = func.date_format(QuantRecord.record_date, '%Y')
        week_part = func.lpad(func.week(QuantRecord.record_date, 1), 2, '0')  # 补零确保两位数
        
        # 连接成 "YYYY-WXX" 格式，如 "2023-W01"
        date_trunc = func.concat(year_part, '-W', week_part)
    else:  # month
        # MySQL 月份格式化 - "YYYY-MM"
        date_trunc = func.date_format(QuantRecord.record_date, '%Y-%m')
    
    # 查询趋势数据
    query = (
        select(
            date_trunc.label("time_period"),
            func.count(QuantRecord.id).label("record_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score")
        )
        .select_from(QuantRecord)
        .join(Student, QuantRecord.student_id == Student.id)
        .where(and_(*conditions))
        .group_by("time_period")
        .order_by("time_period")
    )
    
    result = await db.execute(query)
    trends = []
    
    for row in result:
        trends.append({
            "period": row.time_period,
            "record_count": row.record_count,
            "score_sum": float(row.total_score) if row.total_score else 0,
            "average_score": float(row.avg_score) if row.avg_score else 0
        })
    
    return trends

async def get_item_usage_frequency(
    db: AsyncSession,
    class_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """获取量化项目使用频率"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建基础条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 添加过滤条件
    if class_id:
        conditions.append(Student.class_id == class_id)
    if category:
        conditions.append(QuantItem.category == category)
    
    # 查询项目使用频率
    query = (
        select(
            QuantItem.id.label("item_id"),
            QuantItem.name.label("item_name"),
            QuantItem.category,
            func.count(QuantRecord.id).label("count"),
            func.sum(QuantRecord.score).label("score_sum")
        )
        .select_from(QuantRecord)
        .join(QuantItem, QuantRecord.item_id == QuantItem.id)
        .join(Student, QuantRecord.student_id == Student.id)
        .where(and_(*conditions))
        .group_by(QuantItem.id, QuantItem.name, QuantItem.category)
        .order_by(desc("count"))
        .limit(limit)
    )
    
    result = await db.execute(query)
    usage_data = []
    
    for row in result:
        usage_data.append({
            "item_id": row.item_id,
            "item_name": row.item_name,
            "category": row.category,
            "count": row.count,
            "score_sum": float(row.score_sum) if row.score_sum else 0
        })
    
    return usage_data

async def get_class_comparisons(
    db: AsyncSession,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """获取班级比较数据"""
    # 设置默认日期范围为过去30天
    if not start_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif not end_date:
        end_date = date.today()
    
    # 创建基础条件
    conditions = [
        QuantRecord.record_date >= start_date,
        QuantRecord.record_date <= end_date
    ]
    
    # 添加类别过滤条件
    if category:
        conditions.append(QuantItem.category == category)
    
    # 查询班级比较数据
    query = (
        select(
            Classes.id,
            Classes.name,
            Classes.grade,
            func.count(Student.id.distinct()).label("student_count"),
            func.count(QuantRecord.id).label("record_count"),
            func.sum(QuantRecord.score).label("total_score"),
            func.avg(QuantRecord.score).label("avg_score"),
            func.max(QuantRecord.score).label("max_score"),
            func.min(QuantRecord.score).label("min_score")
        )
        .select_from(QuantRecord)
        .join(Student, QuantRecord.student_id == Student.id)
        .join(Classes, Student.class_id == Classes.id)
        .join(QuantItem, QuantRecord.item_id == QuantItem.id)
        .where(and_(*conditions))
        .group_by(Classes.id, Classes.name, Classes.grade)
        .order_by(desc("total_score"))
    )
    
    result = await db.execute(query)
    comparison_data = []
    
    for row in result:
        comparison_data.append({
            "class_id": row.id,
            "name": row.name,
            "grade": row.grade,
            "student_count": row.student_count,
            "record_count": row.record_count,
            "total_score": float(row.total_score) if row.total_score else 0,
            "avg_score": float(row.avg_score) if row.avg_score else 0,
            "max_score": float(row.max_score) if row.max_score else 0,
            "min_score": float(row.min_score) if row.min_score else 0
        })
    
    return comparison_data

async def get_top_students(
    db: AsyncSession,
    limit: int = 10,
    class_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """获取顶尖学生数据"""
    return await get_student_rankings(
        db, 
        class_id=class_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
