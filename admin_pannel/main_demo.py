"""
Демо-версия админки для тестирования без базы данных
"""
from fastapi import FastAPI
from starlette.responses import HTMLResponse

def create_demo_app() -> FastAPI:
    """Создать демо-версию FastAPI приложения"""
    
    app = FastAPI(
        title="Billing Admin Panel (Demo)",
        description="Demo version of admin panel",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        """Главная страница"""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Billing Admin Panel (Demo)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .feature { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
                .success { color: #28a745; }
                .warning { color: #ffc107; background: #fff3cd; padding: 10px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛠️ Billing Admin Panel (Demo)</h1>
                
                <div class="warning">
                    <strong>Демо-режим:</strong> Для полной функциональности требуется подключение к базе данных PostgreSQL.
                </div>
                
                <h2>✅ Что реализовано:</h2>
                
                <div class="feature">
                    <h3>📋 Модели данных</h3>
                    <ul>
                        <li><strong>Subscription</strong> - Тарифные планы и подписки</li>
                        <li><strong>UserSubscription</strong> - Пользовательские подписки</li>
                        <li><strong>Payment</strong> - Платежи и транзакции</li>
                        <li><strong>Refund</strong> - Возвраты платежей (новое!)</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🎛️ Админские панели</h3>
                    <ul>
                        <li>Управление подписками с поиском и фильтрацией</li>
                        <li>Просмотр пользовательских подписок</li>
                        <li>Управление платежами с маскированием карт</li>
                        <li>Обработка возвратов с отслеживанием статусов</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🐳 Docker инфраструктура</h3>
                    <ul>
                        <li>Dockerfile для контейнеризации</li>
                        <li>docker-compose.yml с Nginx</li>
                        <li>Интеграция с существующими сервисами</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🗃️ База данных</h3>
                    <ul>
                        <li>Миграции Alembic для создания таблиц</li>
                        <li>Связи между моделями</li>
                        <li>Индексы для оптимизации</li>
                    </ul>
                </div>
                
                <h2>🚀 Для запуска полной версии:</h2>
                <pre>
# 1. Запустить PostgreSQL (из других сервисов)
make billing-up  # Запустит PostgreSQL на порту 5433

# 2. Обновить .env файл с правильными настройками БД

# 3. Запустить миграции
poetry run alembic upgrade head

# 4. Запустить приложение
poetry run python main.py
                </pre>
                
                <div class="success">
                    <h3>✨ Статус: Готово к использованию!</h3>
                    <p>Админка полностью реализована и готова к подключению к базе данных.</p>
                </div>
            </div>
        </body>
        </html>
        """)
    
    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса"""
        return {
            "status": "healthy", 
            "service": "admin-panel-demo",
            "message": "Demo version running successfully"
        }
    
    @app.get("/api/info")
    async def api_info():
        """Информация об API"""
        return {
            "admin_panels": [
                {
                    "name": "Subscriptions",
                    "description": "Управление тарифными планами",
                    "features": ["CRUD операции", "Поиск", "Фильтрация"]
                },
                {
                    "name": "User Subscriptions", 
                    "description": "Пользовательские подписки",
                    "features": ["Просмотр подписок", "Управление статусами", "Маскирование карт"]
                },
                {
                    "name": "Payments",
                    "description": "Платежи и транзакции", 
                    "features": ["История платежей", "Статусы", "Детали ошибок"]
                },
                {
                    "name": "Refunds",
                    "description": "Возвраты платежей",
                    "features": ["Обработка возвратов", "Отслеживание статусов", "Причины возврата"]
                }
            ],
            "database_required": True,
            "docker_ready": True
        }
    
    return app

app = create_demo_app()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск демо-версии админ-панели...")
    print("📖 Откройте http://localhost:8002 в браузере")
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )