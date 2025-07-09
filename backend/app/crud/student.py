from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate

class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    async def get_by_student_id_no(
        self, db: AsyncSession, *, student_id_no: str
    ) -> Optional[Student]:
        """根据学号获取学生"""
        query = select(Student).where(Student.student_id_no == student_id_no)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_class(
        self, db: AsyncSession, *, class_id: int, active_only: bool = False
    ) -> List[Student]:
        """获取班级的所有学生"""
        query = select(Student).where(Student.class_id == class_id)
        if active_only:
            query = query.where(Student.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """获取所有活跃学生"""
        query = select(Student).where(Student.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_students_sorted(
        self, 
        db: AsyncSession, 
        *, 
        sort_by: str = "total_score",
        sort_order: str = "desc",
        skip: int = 0, 
        limit: int = 100,
        class_id: Optional[int] = None,
        active_only: bool = False
    ) -> List[Student]:
        """获取排序后的学生列表"""
        query = select(Student)
        
        # 应用筛选条件
        if class_id:
            query = query.where(Student.class_id == class_id)
        if active_only:
            query = query.where(Student.is_active == True)
        
        # 应用排序
        if sort_by == "total_score":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Student.total_score))
            else:
                query = query.order_by(Student.total_score)
        elif sort_by == "rank":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Student.rank))
            else:
                query = query.order_by(Student.rank)
        else:
            # 默认按ID排序
            query = query.order_by(Student.id)
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_scores_and_ranks(
        self, db: AsyncSession, *, class_id: Optional[int] = None
    ) -> int:
        """更新学生的总分和排名"""
        # 首先计算每个学生的总分（实际项目中可能需要更复杂的计算）
        # 这里使用原生SQL，因为它更灵活且直接
        score_update_sql = """
        UPDATE students s
        LEFT JOIN (
            SELECT student_id, SUM(score) as total
            FROM quant_records
            GROUP BY student_id
        ) qr ON s.id = qr.student_id
        SET s.total_score = COALESCE(qr.total, 0)
        """
        
        if class_id:
            score_update_sql += " WHERE s.class_id = :class_id"
            await db.execute(text(score_update_sql), {"class_id": class_id})
        else:
            await db.execute(text(score_update_sql))
        
        # 然后为每个班级更新排名
        if class_id:
            rank_update_sql = """
            SET @rank = 0;
            UPDATE students s
            JOIN (
                SELECT id, (@rank := @rank + 1) as rank_pos
                FROM students
                WHERE class_id = :class_id AND is_active = 1
                ORDER BY total_score DESC
            ) r ON s.id = r.id
            SET s.rank = r.rank_pos
            WHERE s.class_id = :class_id
            """
            await db.execute(text(rank_update_sql), {"class_id": class_id})
        else:
            # 为每个班级单独更新排名
            class_ids_result = await db.execute(
                text("SELECT DISTINCT class_id FROM students WHERE class_id IS NOT NULL")
            )
            class_ids = [row[0] for row in class_ids_result.fetchall()]
            
            for c_id in class_ids:
                rank_update_sql = """
                SET @rank = 0;
                UPDATE students s
                JOIN (
                    SELECT id, (@rank := @rank + 1) as rank_pos
                    FROM students
                    WHERE class_id = :class_id AND is_active = 1
                    ORDER BY total_score DESC
                ) r ON s.id = r.id
                SET s.rank = r.rank_pos
                WHERE s.class_id = :class_id
                """
                await db.execute(text(rank_update_sql), {"class_id": c_id})
        
        await db.commit()
        
        # 返回更新的学生数量
        updated_count_result = await db.execute(
            text("SELECT COUNT(*) FROM students WHERE total_score IS NOT NULL")
        )
        return updated_count_result.scalar_one()

    async def get_students_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "id",
        sort_order: str = "asc"
    ) -> Tuple[List[Student], int]:
        """
        根据多个过滤条件获取学生列表
        
        支持的过滤条件:
        - class_id: 班级ID (精确匹配)
        - name: 学生姓名 (模糊匹配)
        - student_id_no: 学号 (模糊匹配)
        - gender: 性别 (精确匹配)
        - is_active: 是否启用 (精确匹配)
        """
        # 构建基本查询
        query = select(Student)
        count_query = select(func.count(Student.id))
        
        # 应用过滤条件
        if filters:
            # 班级ID过滤
            if "class_id" in filters and filters["class_id"] is not None:
                query = query.where(Student.class_id == filters["class_id"])
                count_query = count_query.where(Student.class_id == filters["class_id"])
            
            # 姓名模糊搜索
            if "name" in filters and filters["name"]:
                name_filter = f"%{filters['name']}%"
                query = query.where(Student.full_name.like(name_filter))
                count_query = count_query.where(Student.full_name.like(name_filter))
            
            # 学号模糊搜索
            if "student_id_no" in filters and filters["student_id_no"]:
                id_no_filter = f"%{filters['student_id_no']}%"
                query = query.where(Student.student_id_no.like(id_no_filter))
                count_query = count_query.where(Student.student_id_no.like(id_no_filter))
            
            # 性别过滤
            if "gender" in filters and filters["gender"]:
                query = query.where(Student.gender == filters["gender"])
                count_query = count_query.where(Student.gender == filters["gender"])
            
            # 状态过滤
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.where(Student.is_active == filters["is_active"])
                count_query = count_query.where(Student.is_active == filters["is_active"])
        
        # 获取总记录数
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        
        # 应用排序
        if sort_by == "total_score":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Student.total_score))
            else:
                query = query.order_by(Student.total_score)
        elif sort_by == "rank":
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Student.rank))
            else:
                query = query.order_by(Student.rank)
        else:
            # 默认按ID排序
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Student.id))
            else:
                query = query.order_by(Student.id)
        
        # 应用分页
        query = query.offset(skip).limit(limit)
        
        # 执行查询
        result = await db.execute(query)
        students = result.scalars().all()
        
        return students, total

# 创建全局学生CRUD实例
student = CRUDStudent(Student)
