import asyncio
import random
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import text, select

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 确保可以找到.env文件
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session, engine
from sqlalchemy.sql import select

from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.models.classes import Classes
from app.models.student import Student
from app.models.quant_item import QuantItem
from app.models.quant_item_category import QuantItemCategory
from app.models.quant_record import QuantRecord
from app.models.notification import Notification
from app.models.ai_conversation import AIConversation, AIMessage

async def init_test_data():
    """初始化测试数据"""
    print("开始初始化测试数据...")
    
    db = async_session()
    try:
        # 创建角色
        roles = await create_roles(db)
        
        # 创建班级
        classes = await create_classes(db)
        
        # 创建用户
        users = await create_users(db, roles, classes)
        
        # 创建学生
        students = await create_students(db, classes, users)
        
        # 创建量化项目分类
        categories = await create_quant_item_categories(db)
        
        # 创建量化项目
        items = await create_quant_items(db)
        
        # 创建量化记录
        records = await create_quant_records(db, students, items, users)
        
        # 创建通知
        notifications = await create_notifications(db, users, roles)
        
        # 创建AI对话
        conversations = await create_ai_conversations(db, users)
    
        print("测试数据初始化完成！")
    finally:
        await db.close()

async def create_roles(db: AsyncSession) -> list[Role]:
    """创建角色"""
    print("创建角色...")
    
    # 先检查角色是否已存在
    existing_roles = (await db.execute(
        text("SELECT name FROM roles")
    )).fetchall()
    existing_role_names = [role[0] for role in existing_roles]
    print(f"已存在角色: {existing_role_names}")
    
    roles = [
        Role(name="admin", description="系统管理员"),
        Role(name="teacher", description="教师"),
        Role(name="student", description="学生"),
        Role(name="parent", description="家长")
    ]
    
    # 过滤掉已存在的角色
    roles_to_add = [role for role in roles if role.name not in existing_role_names]
    
    if roles_to_add:
        db.add_all(roles_to_add)
        await db.commit()
        print(f"创建了 {len(roles_to_add)} 个新角色")
    
    # 获取所有角色（包括已存在的）
    all_roles = (await db.execute(
        text("SELECT id, name FROM roles")
    )).fetchall()
    
    roles = []
    for role_id, role_name in all_roles:
        role = await db.get(Role, role_id)
        roles.append(role)
    
    print(f"总共有 {len(roles)} 个角色")
    return roles

async def create_classes(db: AsyncSession) -> list[Classes]:
    """创建班级"""
    print("创建班级...")
    
    # 先检查班级是否已存在
    existing_classes = (await db.execute(
        text("SELECT name FROM classes")
    )).fetchall()
    existing_class_names = [cls[0] for cls in existing_classes]
    print(f"已存在班级: {existing_class_names}")
    
    classes = [
        Classes(name="一年级1班", grade="一年级", year=2023),
        Classes(name="一年级2班", grade="一年级", year=2023),
        Classes(name="二年级1班", grade="二年级", year=2022),
        Classes(name="二年级2班", grade="二年级", year=2022),
        Classes(name="三年级1班", grade="三年级", year=2021)
    ]
    
    # 过滤掉已存在的班级
    classes_to_add = [cls for cls in classes if cls.name not in existing_class_names]
    
    if classes_to_add:
        db.add_all(classes_to_add)
        await db.commit()
        print(f"创建了 {len(classes_to_add)} 个新班级")
    
    # 获取所有班级（包括已存在的）
    all_classes = (await db.execute(
        text("SELECT id, name FROM classes")
    )).fetchall()
    
    classes = []
    for class_id, class_name in all_classes:
        class_obj = await db.get(Classes, class_id)
        classes.append(class_obj)
    
    print(f"总共有 {len(classes)} 个班级")
    return classes

async def create_users(db: AsyncSession, roles: list[Role], classes: list[Classes]) -> list[User]:
    """创建用户"""
    print("创建用户...")
    
    # 检查用户是否已存在
    existing_users = (await db.execute(
        text("SELECT username FROM users")
    )).fetchall()
    existing_usernames = [user[0] for user in existing_users]
    print(f"已存在用户: {existing_usernames}")
    
    # 获取角色ID
    admin_role = next(role for role in roles if role.name == "admin")
    teacher_role = next(role for role in roles if role.name == "teacher")
    student_role = next(role for role in roles if role.name == "student")
    parent_role = next(role for role in roles if role.name == "parent")
    
    users = [
        # 管理员
        User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            full_name="系统管理员",
            role_id=admin_role.id,
            is_active=True
        ),
        
        # 教师
        User(
            username="teacher1",
            password_hash=get_password_hash("teacher123"),
            full_name="张老师",
            role_id=teacher_role.id,
            is_active=True
        ),
        User(
            username="teacher2",
            password_hash=get_password_hash("teacher123"),
            full_name="王老师",
            role_id=teacher_role.id,
            is_active=True
        ),
        
        # 学生用户 (对应部分学生)
        User(
            username="student1",
            password_hash=get_password_hash("student123"),
            full_name="李明",
            role_id=student_role.id,
            class_id=classes[0].id,
            is_active=True
        ),
        User(
            username="student2",
            password_hash=get_password_hash("student123"),
            full_name="赵阳",
            role_id=student_role.id,
            class_id=classes[1].id,
            is_active=True
        ),
        
        # 家长
        User(
            username="parent1",
            password_hash=get_password_hash("parent123"),
            full_name="王璐父亲",
            role_id=parent_role.id,
            is_active=True
        )
    ]
    
    # 过滤掉已存在的用户
    users_to_add = [user for user in users if user.username not in existing_usernames]
    
    if users_to_add:
        db.add_all(users_to_add)
        await db.commit()
        print(f"创建了 {len(users_to_add)} 个新用户")
    
    # 获取所有用户（包括已存在的）
    all_users = []
    for username in set([user.username for user in users]):
        user_result = await db.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        )
        user_id = user_result.scalar_one()
        user = await db.get(User, user_id)
        all_users.append(user)
    
    # 更新班级的班主任
    teacher1 = next((u for u in all_users if u.username == "teacher1"), None)
    teacher2 = next((u for u in all_users if u.username == "teacher2"), None)
    
    if teacher1 and teacher2:
        classes[0].head_teacher_id = teacher1.id  # 张老师是一年级1班的班主任
        classes[1].head_teacher_id = teacher2.id  # 王老师是一年级2班的班主任
    await db.commit()
    
    print(f"总共有 {len(all_users)} 个用户")
    return all_users

async def create_students(db: AsyncSession, classes: list[Classes], users: list[User]) -> list[Student]:
    """创建学生"""
    print("创建学生...")
    
    # 检查学生是否已存在
    existing_students = (await db.execute(
        text("SELECT student_id_no FROM students")
    )).fetchall()
    existing_student_ids = [student[0] for student in existing_students]
    print(f"已存在学生ID: {len(existing_student_ids)}")

    students = []
    
    # 找到学生用户
    student_users = [user for user in users if user.role.name == "student"]
    
    # 为学生用户创建对应的学生记录
    for i, user in enumerate(student_users):
        student_id_no = f"S{2023000 + i + 1}"
        if student_id_no in existing_student_ids:
            continue
            
        students.append(
            Student(
                student_id_no=f"S{2023000 + i + 1}",
                full_name=user.full_name,
                gender="male" if i % 2 == 0 else "female",
                birth_date=datetime.now(timezone.utc) - timedelta(days=365 * (6 + i % 3)),
                class_id=user.class_id,
                user_id=user.id,
                phone=f"1380013{i+1:04d}",
                email=f"student{i+1}@example.com",
                contact_info=f"住址：测试地址{i+1}号",
                avatar_url=f"/static/avatars/student{i%5+1}.jpg",
                is_active=True
            )
        )
    
    # 创建额外的学生（没有用户账号）
    for i in range(20):
        student_id_no = f"S{2023000 + len(student_users) + i + 1}"
        if student_id_no in existing_student_ids:
            continue
            
        class_id = classes[i % len(classes)].id
        gender = "male" if i % 2 == 0 else "female"
        name = ["小明", "小红", "小张", "小李", "小王"][i % 5]
        last_name = ["李", "张", "王", "赵", "刘"][i % 5]
        
        students.append(
            Student(
                student_id_no=f"S{2023000 + len(student_users) + i + 1}",
                full_name=f"{last_name}{name}{i+1}",
                gender=gender,
                birth_date=datetime.now(timezone.utc) - timedelta(days=365 * (6 + i % 3)),
                class_id=class_id,
                phone=f"1370013{i+1:04d}",
                email=f"student{len(student_users)+i+1}@example.com",
                contact_info=f"住址：测试地址{i+1}号",
                avatar_url=f"/static/avatars/student{i%5+1}.jpg",
                is_active=True
            )
        )
    
    if students:
        db.add_all(students)
        await db.commit()
        print(f"创建了 {len(students)} 个新学生")
    else:
        print("没有新学生需要创建")
    
    # 获取所有学生
    all_students = (await db.execute(
        text("SELECT id FROM students")
    )).fetchall()
    
    students = [await db.get(Student, student_id[0]) for student_id in all_students]
    print(f"总共有 {len(students)} 个学生")
    return students

async def create_quant_items(db: AsyncSession) -> list[QuantItem]:
    """创建量化项目"""
    print("创建量化项目...")
    
    # 检查量化项目是否已存在
    existing_items = (await db.execute(
        text("SELECT name FROM quant_items")
    )).fetchall()
    existing_item_names = [item[0] for item in existing_items]
    print(f"已存在量化项目: {existing_item_names}")
    
    # 查询已存在的分类
    categories = (await db.execute(
        text("SELECT id, name FROM quant_item_categories")
    )).fetchall()
    category_map = {cat[1]: cat[0] for cat in categories}
    print(f"分类ID映射: {category_map}")

    items = [
        # 行为习惯类
        QuantItem(
            name="按时完成作业",
            description="学生能够按时完成所布置的作业",
            min_score=0,
            max_score=5,
            default_score=2.0,
            default_reason="能够认真完成作业",
            weight=1.0,
            category="行为习惯",
            category_id=category_map.get("行为习惯"),
            is_active=True
        ),
        QuantItem(
            name="课堂认真听讲",
            description="学生在课堂上认真听讲，积极回答问题",
            min_score=0,
            max_score=5,
            default_score=1.5,
            default_reason="上课表现积极",
            weight=1.0,
            category="行为习惯",
            category_id=category_map.get("行为习惯"),
            is_active=True
        ),
        QuantItem(
            name="保持教室整洁",
            description="学生主动参与教室清洁，保持环境整洁",
            min_score=0,
            max_score=3,
            default_score=1.0,
            default_reason="积极整理教室",
            weight=1.0,
            category="行为习惯",
            category_id=category_map.get("行为习惯"),
            is_active=True
        ),
        
        # 学习表现类
        QuantItem(
            name="考试成绩优秀",
            description="学生在考试中取得优秀成绩",
            min_score=0,
            max_score=10,
            default_score=3.0,
            default_reason="考试成绩优异",
            weight=1.5,
            category="学习表现",
            category_id=category_map.get("学习表现"),
            is_active=True
        ),
        QuantItem(
            name="积极参与课外活动",
            description="学生积极参与各类课外学习活动",
            min_score=0,
            max_score=5,
            default_score=1.5,
            default_reason="参与学校活动",
            weight=1.0,
            category="学习表现",
            category_id=category_map.get("学习表现"),
            is_active=True
        ),
        
        # 品德表现类
        QuantItem(
            name="助人为乐",
            description="学生乐于助人，关心同学",
            min_score=0,
            max_score=5,
            default_score=2.0,
            default_reason="主动帮助他人",
            weight=1.0,
            category="品德表现",
            category_id=category_map.get("品德表现"),
            is_active=True
        ),
        QuantItem(
            name="诚实守信",
            description="学生言行一致，诚实守信",
            min_score=0,
            max_score=5,
            default_score=1.5,
            default_reason="诚实可信",
            weight=1.0,
            category="品德表现",
            category_id=category_map.get("品德表现"),
            is_active=True
        ),
        
        # 违纪行为类（负分项）
        QuantItem(
            name="课堂扰乱秩序",
            description="学生在课堂上扰乱秩序",
            min_score=-5,
            max_score=0,
            default_score=-2.0,
            default_reason="上课扰乱秩序",
            weight=1.0,
            category="违纪行为",
            category_id=category_map.get("违纪行为"),
            is_active=True
        ),
        QuantItem(
            name="迟到",
            description="学生上课迟到",
            min_score=-3,
            max_score=0,
            default_score=-1.0,
            default_reason="上课迟到",
            weight=1.0,
            category="违纪行为",
            category_id=category_map.get("违纪行为"),
            is_active=True
        ),
        QuantItem(
            name="打架斗殴",
            description="学生参与打架斗殴事件",
            min_score=-10,
            max_score=0,
            default_score=-5.0,
            default_reason="参与打架行为",
            weight=1.5,
            category="违纪行为",
            category_id=category_map.get("违纪行为"),
            is_active=True
        )
    ]
    
    # 过滤掉已存在的项目
    items_to_add = [item for item in items if item.name not in existing_item_names]
    
    if items_to_add:
        db.add_all(items_to_add)
        await db.commit()
        print(f"创建了 {len(items_to_add)} 个新量化项目")
    else:
        print("没有新量化项目需要创建")
    
    # 获取所有量化项目
    all_items = (await db.execute(
        text("SELECT id FROM quant_items")
    )).fetchall()
    
    items = [await db.get(QuantItem, item_id[0]) for item_id in all_items]
    print(f"总共有 {len(items)} 个量化项目")
    return items

async def create_quant_records(
    db: AsyncSession, 
    students: list[Student], 
    items: list[QuantItem],
    users: list[User]
) -> list[QuantRecord]:
    """创建量化记录"""
    print("创建量化记录...")
    
    # 找到教师用户
    teachers = [user for user in users if user.role.name == "teacher"]
    
    records = []
    # 为每个学生创建多条记录
    for student in students:
        # 每个学生创建3-8条记录
        for _ in range(random.randint(3, 8)):
            # 随机选择一个量化项目
            item = random.choice(items)
            # 随机选择一个教师作为记录者
            teacher = random.choice(teachers)
            
            # 随机日期 (过去30天内)
            record_date = datetime.now(timezone.utc).date() - timedelta(days=random.randint(0, 30))
            
            # 记录分数 (基于项目默认分数上下浮动)
            score = float(item.default_score) + random.uniform(-0.5, 0.5)
            
            # 随机备注
            reasons = [
                "表现非常好",
                "继续努力",
                "需要改进",
                "进步明显",
                "再接再厉",
                None  # 部分记录没有备注
            ]
            
            records.append(
                QuantRecord(
                    student_id=student.id,
                    item_id=item.id,
                    score=score,
                    record_date=record_date,
                    reason=random.choice(reasons),
                    recorder_id=teacher.id
                )
            )
    
    db.add_all(records)
    await db.commit()
    
    print(f"创建了 {len(records)} 条量化记录")
    return records

async def create_notifications(
    db: AsyncSession,
    users: list[User],
    roles: list[Role]
) -> list[Notification]:
    """创建通知消息"""
    print("创建通知...")
    
    # 检查已存在的通知
    existing_notifications = (await db.execute(
        text("SELECT title FROM notifications")
    )).fetchall()
    existing_titles = [notification[0] for notification in existing_notifications]
    print(f"已存在通知: {len(existing_titles)}")
    
    # 找到管理员和教师
    admin = next(user for user in users if user.role.name == "admin")
    teachers = [user for user in users if user.role.name == "teacher"]
    
    # 找到学生角色ID
    student_role = next(role for role in roles if role.name == "student")
    
    notifications = [
        # 系统公告 - 发给所有人
        Notification(
            title="系统更新通知",
            content="亲爱的用户，系统将于本周日凌晨2点-4点进行例行维护，请合理安排使用时间。",
            notification_type="system",
            sender_id=admin.id,
            is_read=False
        ),
        
        # 角色通知 - 发给特定角色
        Notification(
            title="学生量化评分规则更新",
            content="各位同学注意，学校量化评分规则已更新，请查看附件了解详情。",
            notification_type="role",
            sender_id=admin.id,
            recipient_role_id=student_role.id,
            is_read=False
        ),
        
        # 个人通知 - 发给特定用户
        Notification(
            title="作业完成情况反馈",
            content="您的孩子最近作业完成情况良好，希望继续保持。",
            notification_type="personal",
            sender_id=teachers[0].id,
            recipient_user_id=users[-1].id,  # 发给家长
            is_read=False
        )
    ]
    
    # 过滤掉已存在的通知
    notifications_to_add = [notification for notification in notifications 
                           if notification.title not in existing_titles]
    
    if notifications_to_add:
        db.add_all(notifications_to_add)
        await db.commit()
        print(f"创建了 {len(notifications_to_add)} 条新通知")
    else:
        print("没有新通知需要创建")
    
    # 获取所有通知
    all_notifications = (await db.execute(
        text("SELECT id FROM notifications")
    )).fetchall()
    
    notifications = [await db.get(Notification, notification_id[0]) for notification_id in all_notifications]
    print(f"总共有 {len(notifications)} 条通知")
    return notifications

async def create_ai_conversations(db: AsyncSession, users: list[User]) -> list[AIConversation]:
    """创建AI对话和消息"""
    print("创建AI对话和消息...")
    
    # 检查已存在的AI对话
    existing_conversations = (await db.execute(
        text("SELECT title FROM ai_conversations")
    )).fetchall()
    existing_titles = [conversation[0] for conversation in existing_conversations]
    print(f"已存在AI对话: {len(existing_titles)}")
    
    conversations = []
    messages = []
    
    # 为每个用户创建对话
    for i, user in enumerate(users[:3]):  # 只为前3个用户创建对话
        # 创建两个对话
        # 第一个对话 - 关于学生成绩
        conversation_title1 = f"关于学生成绩的对话 - {user.username}"
        if conversation_title1 not in existing_titles:
            conv1 = AIConversation(
                user_id=user.id,
                title=conversation_title1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(conv1)
            await db.flush()  # 立即获取对话ID
            conversations.append(conv1)
            
            # 为第一个对话添加消息
            messages.extend([
                AIMessage(
                    conversation_id=conv1.id,
                    role="user",
                    content="我想了解如何查看学生成绩",
                    created_at=datetime.utcnow() - timedelta(minutes=30)
                ),
                AIMessage(
                    conversation_id=conv1.id,
                    role="assistant",
                    content="您可以在'学生管理'页面选择班级和学生，然后点击'查看成绩'按钮来查看学生的成绩详情。",
                    created_at=datetime.utcnow() - timedelta(minutes=29)
                )
            ])
        
        # 第二个对话 - 关于系统使用
        conversation_title2 = f"系统功能使用指南 - {user.username}"
        if conversation_title2 not in existing_titles:
            conv2 = AIConversation(
                user_id=user.id,
                title=conversation_title2,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(conv2)
            await db.flush()  # 立即获取对话ID
            conversations.append(conv2)
            
            # 为第二个对话添加消息
            messages.extend([
                AIMessage(
                    conversation_id=conv2.id,
                    role="user",
                    content="如何创建新的量化项目？",
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ),
                AIMessage(
                    conversation_id=conv2.id,
                    role="assistant",
                    content="创建新的量化项目需要管理员或教师权限。您可以进入'量化项目'页面，点击'新建项目'按钮。",
                    created_at=datetime.utcnow() - timedelta(hours=2, minutes=1)
                )
            ])
    
    if conversations:
        print(f"创建了 {len(conversations)} 个新AI对话")
    else:
        print("没有新AI对话需要创建")
    
    if messages:
        db.add_all(messages)
        await db.commit()
        print(f"创建了 {len(messages)} 条新AI消息")
    else:
        print("没有新AI消息需要创建")
    
    # 获取所有AI对话
    all_conversations = (await db.execute(
        select(AIConversation)
    )).scalars().all()
    
    print(f"总共有 {len(all_conversations)} 个AI对话")
    return list(all_conversations)

async def create_quant_item_categories(db: AsyncSession) -> list[QuantItemCategory]:
    """创建量化项目分类"""
    print("创建量化项目分类...")
    
    # 检查量化项目分类是否已存在
    existing_categories = (await db.execute(
        text("SELECT name FROM quant_item_categories")
    )).fetchall()
    existing_category_names = [category[0] for category in existing_categories]
    print(f"已存在量化项目分类: {existing_category_names}")

    categories = [
        QuantItemCategory(
            name="行为习惯",
            description="学生日常行为习惯相关的量化项目",
            order=1,
            is_active=True
        ),
        QuantItemCategory(
            name="学习表现",
            description="学生学习过程和结果相关的量化项目",
            order=2,
            is_active=True
        ),
        QuantItemCategory(
            name="品德表现",
            description="学生品德和道德素养相关的量化项目",
            order=3,
            is_active=True
        ),
        QuantItemCategory(
            name="违纪行为",
            description="学生违反校规校纪的行为",
            order=4,
            is_active=True
        )
    ]
    
    # 过滤掉已存在的分类
    categories_to_add = [category for category in categories if category.name not in existing_category_names]
    
    if categories_to_add:
        db.add_all(categories_to_add)
        await db.commit()
        print(f"创建了 {len(categories_to_add)} 个新量化项目分类")
    else:
        print("没有新量化项目分类需要创建")
    
    # 获取所有量化项目分类
    all_categories = (await db.execute(
        text("SELECT id FROM quant_item_categories")
    )).fetchall()
    
    categories = [await db.get(QuantItemCategory, category_id[0]) for category_id in all_categories]
    print(f"总共有 {len(categories)} 个量化项目分类")
    return categories

async def main():
    """主函数"""
    try:
        await init_test_data()
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