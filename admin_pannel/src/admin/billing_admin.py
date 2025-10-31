from sqladmin import ModelView

from src.models.billing import (
    Subscription,
    UserSubscription,
    Payment,
    Refund,
)


class SubscriptionAdmin(ModelView, model=Subscription):
    """Админское представление для подписок"""

    name = "Subscription"
    name_plural = "Subscriptions"
    icon = "fa-solid fa-credit-card"

    column_list = [
        "id",
        "title",
        "description",
        "period",
        "sum",
        "repeatition",
        "repeats_number"
    ]

    # Колонки для поиска
    column_searchable_list = ["title", "description"]

    # Фильтры
    column_filters = ["repeatition", "sum"]

    # Сортировка по умолчанию
    column_default_sort = "id"

    # Детали формы
    column_details_exclude_list = []

    # Форма создания/редактирования
    form_columns = [
        "title",
        "description",
        "period",
        "sum",
        "repeatition",
        "repeats_number"
    ]

    # Валидация
    form_args = {
        "title": {"validators": []},
        "sum": {"validators": []},
        "period": {"validators": []},
    }


class UserSubscriptionAdmin(ModelView, model=UserSubscription):
    """Админское представление для пользовательских подписок"""

    name = "User Subscription"
    name_plural = "User Subscriptions"
    icon = "fa-solid fa-users"

    column_list = [
        "id",
        "user_id",
        "subscription_id",
        "status"
    ]

    # Колонки для поиска
    column_searchable_list = ["user_id", "subscription_id"]

    # Фильтры
    column_filters = [
        "status"
    ]

    # Сортировка по умолчанию
    column_default_sort = "id"

    form_columns = [
        "user_id",
        "subscription_id",
        "status"
    ]


class PaymentAdmin(ModelView, model=Payment):
    """Админское представление для платежей"""

    name = "Payment"
    name_plural = "Payments"
    icon = "fa-solid fa-money-bill"
    column_list = [
        "id",
        "user_subscription_id",
        "amount",
        "status",
        "created_at"
    ]

    # Колонки для поиска по ID
    column_searchable_list = ["user_subscription_id"]

    # Фильтры
    column_filters = [
        "status",
        "created_at",
        "amount"
    ]

    # Сортировка по умолчанию
    column_default_sort = ("created_at", True)

    form_columns = [
        "user_subscription_id",
        "amount",
        "status",
        "created_at"
    ]

    column_formatters = {
        "amount": lambda m, a: f"${m.amount:.2f}" if m.amount else "",
    }

    form_widget_args = {
        "created_at": {"readonly": True},
    }


class RefundAdmin(ModelView, model=Refund):
    """Админское представление для возвратов"""

    name = "Refund"
    name_plural = "Refunds"
    icon = "fa-solid fa-undo"

    column_list = [
        "id",
        "payment_id",
        "amount",
        "status",
        "created_at",
        "processed_at"
    ]

    # Колонки для поиска
    column_searchable_list = ["external_refund_id", "payment_id"]

    # Фильтры
    column_filters = [
        "status",
        "created_at",
        "processed_at",
        "amount"
    ]

    # Сортировка по умолчанию
    column_default_sort = ("created_at", True)

    # Форма создания/редактирования
    form_columns = [
        "payment_id",
        "amount",
        "status",
        "external_refund_id",
        "reason",
        "created_at",
        "processed_at",
        "error_details"
    ]

    # Форматирование колонок
    column_formatters = {
        "amount": lambda m, a: f"${m.amount:.2f}" if m.amount else "",
        "reason": lambda m, a: (m.reason[:50] + "...") if m.reason and len(m.reason) > 50 else m.reason,
        "error_details": lambda m, a: (m.error_details[:50] + "...") if m.error_details and len(m.error_details) > 50 else m.error_details,
    }

    # Только чтение для некоторых полей
    form_widget_args = {
        "external_refund_id": {"readonly": True},
        "created_at": {"readonly": True},
    }
