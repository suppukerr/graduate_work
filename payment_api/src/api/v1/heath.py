from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth_depends import get_current_user
from src.db.postgres import get_db

router = APIRouter(prefix="/api/v1/payment/health", tags=["health"])


@router.get("/service")
async def health_check():
    """Проверка состояния сервиса"""
    print('чек-чек')
    return {"status": "ok", "service": "billing-api"}


@router.get("/service-auth")
async def health_check_auth(current_user=Depends(get_current_user)):
    """Проверка состояния сервиса"""
    return {"status": "ok", "service": "billing-api"}


@router.get("/db")
async def database_check(db: AsyncSession = Depends(get_db)):
    """Проверка подключения к базе данных PostgreSQL"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "postgresql", "connection": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )
