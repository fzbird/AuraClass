from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import time
import uuid
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import DB_CONNECTION_POOL_SIZE

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
    # 添加连接池回收参数，确保连接不会被长时间保持
    pool_recycle=3600
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # 使用更安全的事务隔离级别
    future=True
)

logger = get_logger(__name__)

# 跟踪活动会话
active_sessions = {}

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    session: Optional[AsyncSession] = None
    session_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # 创建新会话
        session = async_session()
        # 记录会话创建
        active_sessions[session_id] = {
            'created_at': start_time,
            'status': 'active'
        }
        logger.debug(f"Session {session_id} created. Active sessions: {len(active_sessions)}")
        
        # 确保会话处于干净状态
        try:
            # 显式关闭任何可能存在的事务
            await session.rollback()
            logger.debug(f"Session {session_id} rollback performed during initialization")
        except Exception as e:
            logger.warning(f"Session {session_id} rollback during init failed: {str(e)}")
        
        # 更新连接池指标
        DB_CONNECTION_POOL_SIZE.set(engine.pool.size())
        
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)} [session.py/{__name__}/get_db:{e.__traceback__.tb_lineno}]")
        if session:
            try:
                # 确保事务回滚
                await session.rollback()
                logger.debug(f"Session {session_id} rolled back due to error")
            except Exception as rollback_error:
                logger.error(f"Rollback failed for session {session_id}: {str(rollback_error)}")
        raise
    finally:
        if session:
            try:
                # 确保会话关闭
                await session.close()
                logger.debug(f"Session {session_id} closed after {time.time() - start_time:.2f}s")
            except Exception as close_error:
                logger.error(f"Failed to close session {session_id}: {str(close_error)}")
        
        # 从活动会话中移除
        if session_id in active_sessions:
            del active_sessions[session_id]
            logger.debug(f"Session {session_id} removed from tracking. Remaining: {len(active_sessions)}")

async def check_db_connection(db: AsyncSession) -> bool:
    """检查数据库连接状态"""
    try:
        # 执行简单查询测试连接
        result = await db.execute(text("SELECT 1"))
        value = result.scalar_one()
        logger.info(f"Database connection check successful: {value}")
        return value == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        # 记录额外的连接池信息
        try:
            pool_size = engine.pool.size()
            logger.error(f"Current pool size: {pool_size}")
        except Exception as pool_error:
            logger.error(f"Error getting pool info: {str(pool_error)}")
        return False

# 带有事务保护的会话上下文管理器
@asynccontextmanager
async def safe_db_transaction():
    """安全的事务上下文管理器，确保事务的完整性和清理"""
    session_id = str(uuid.uuid4())
    session = None
    
    try:
        session = async_session()
        # 确保以干净状态开始
        await session.rollback()
        logger.debug(f"Transaction {session_id} starting with clean session")
        
        # 开始新事务
        async with session.begin():
            # 提供会话给调用者
            yield session
            # 事务自动提交或回滚
        
        logger.debug(f"Transaction {session_id} completed successfully")
    except Exception as e:
        logger.error(f"Transaction {session_id} failed: {str(e)}")
        # session.begin() 上下文会自动回滚
        raise
    finally:
        if session:
            try:
                # 确保会话关闭
                await session.close()
                logger.debug(f"Transaction session {session_id} closed")
            except Exception as close_error:
                logger.error(f"Failed to close transaction session {session_id}: {str(close_error)}")

async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """异步会话上下文管理器"""
    session_id = str(uuid.uuid4())
    async with async_session() as session:
        try:
            # 确保以干净状态开始
            await session.rollback()
            logger.debug(f"Context session {session_id} starting with clean state")
            
            yield session
            await session.commit()
            logger.debug(f"Context session {session_id} committed")
        except Exception as e:
            logger.error(f"Context session {session_id} error: {str(e)}")
            await session.rollback()
            logger.debug(f"Context session {session_id} rolled back")
            raise
        finally:
            logger.debug(f"Context session {session_id} finished")
