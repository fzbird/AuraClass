import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import async_session, engine

async def update_category_ids():
    """更新量化项目的分类ID"""
    print("开始更新量化项目分类ID...")
    
    db = async_session()
    try:
        # 获取所有分类
        categories = (await db.execute(
            text("SELECT id, name FROM quant_item_categories")
        )).fetchall()
        
        category_map = {cat[1]: cat[0] for cat in categories}
        print(f"分类映射: {category_map}")
        
        # 更新每个分类的量化项目
        for category_name, category_id in category_map.items():
            result = await db.execute(
                text("UPDATE quant_items SET category_id = :category_id WHERE category = :category_name"),
                {"category_id": category_id, "category_name": category_name}
            )
            await db.commit()
            print(f"已更新 {category_name} 类别的量化项目")
        
        # 统计更新结果
        total_updated = (await db.execute(
            text("SELECT COUNT(*) FROM quant_items WHERE category_id IS NOT NULL")
        )).scalar_one()
        
        total_items = (await db.execute(
            text("SELECT COUNT(*) FROM quant_items")
        )).scalar_one()
        
        print(f"总共更新了 {total_updated}/{total_items} 个量化项目的分类ID")
        
        print("量化项目分类ID更新完成！")
    finally:
        await db.close()

async def main():
    """主函数"""
    try:
        await update_category_ids()
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