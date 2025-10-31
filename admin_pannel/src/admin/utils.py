"""Утилиты для настройки админ-панели"""

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy import Engine

from src.admin.billing_admin import (
    SubscriptionAdmin,
    UserSubscriptionAdmin,
    PaymentAdmin,
    RefundAdmin
)


def setup_admin(app: FastAPI, engine: Engine) -> Admin:
    """
    Настройка и регистрация админ-панели

    Args:
        app: FastAPI приложение
        engine: SQLAlchemy engine

    Returns:
        Admin: Настроенная админ-панель
    """
    admin = Admin(app, engine)

    # Регистрация всех админских представлений
    admin.add_view(SubscriptionAdmin)
    admin.add_view(UserSubscriptionAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(RefundAdmin)

    return admin
