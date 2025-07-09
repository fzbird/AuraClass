import asyncio
import sys
import os
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import async_session, engine

async def update_student_fields():
    """更新学生的新字段值"""
    print("开始更新学生字段...")
    
    db = async_session()
    try:
        # 获取所有学生ID
        students = (await db.execute(
            text("SELECT id, student_id_no FROM students")
        )).fetchall()
        
        print(f"找到 {len(students)} 名学生")
        
        # 更新每个学生的字段
        for i, (student_id, student_id_no) in enumerate(students):
            idx = int(student_id_no.replace("S", "")) % 5  # 使用学号作为随机种子
            
            # 更新电话和邮箱
            phone = f"138{i:08d}"
            email = f"student{student_id_no.replace('S', '')}@example.com"
            
            # 更新头像URL
            avatar_url = f"/static/avatars/student{idx+1}.jpg"
            
            # 更新激活状态（95%的概率为活跃状态）
            is_active = random.random() < 0.95
            
            # 执行更新
            await db.execute(
                text("""
                UPDATE students 
                SET phone = :phone, 
                    email = :email, 
                    avatar_url = :avatar_url, 
                    is_active = :is_active 
                WHERE id = :student_id
                """),
                {
                    "student_id": student_id,
                    "phone": phone,
                    "email": email,
                    "avatar_url": avatar_url,
                    "is_active": is_active
                }
            )
            
            if i % 10 == 0:  # 每10条提交一次事务
                await db.commit()
                print(f"已更新 {i+1}/{len(students)} 名学生")
        
        # 最终提交
        await db.commit()
        
        # 更新学生分数和排名
        print("更新学生分数和排名...")
        
        # 先计算总分
        await db.execute(text("""
        UPDATE students s
        LEFT JOIN (
            SELECT student_id, SUM(score) as total
            FROM quant_records
            GROUP BY student_id
        ) qr ON s.id = qr.student_id
        SET s.total_score = COALESCE(qr.total, 0)
        """))
        
        # 获取所有班级
        class_ids = (await db.execute(
            text("SELECT DISTINCT class_id FROM students WHERE class_id IS NOT NULL")
        )).fetchall()
        
        # 为每个班级更新排名
        for (class_id,) in class_ids:
            await db.execute(text("""
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
            """), {"class_id": class_id})
        
        await db.commit()
        
        print("学生字段更新完成！")
    finally:
        await db.close()

async def main():
    """主函数"""
    try:
        await update_student_fields()
    finally:
        # 确保关闭数据库连接
        await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}") 