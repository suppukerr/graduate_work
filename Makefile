.PHONY: help infra infra-up infra-down infra-logs infra-clean auth auth-up auth-down auth-logs auth-build auth-clean billing billing-up billing-down billing-logs billing-build billing-clean payment payment-up payment-down payment-logs payment-build payment-clean admin admin-up admin-down admin-logs admin-build admin-clean all-up all-down

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========================================
# INFRASTRUCTURE
# ========================================
infra: ## 🏗️  Infrastructure
	@echo "Доступные команды для Infrastructure:"
	@echo "  make infra-up     - Запустить инфраструктуру (Kafka)"
	@echo "  make infra-down   - Остановить инфраструктуру"
	@echo "  make infra-logs   - Показать логи Kafka"
	@echo "  make infra-clean  - Удалить контейнеры и volumes"

infra-up: ## ├── Запустить инфраструктуру
	cd infra && docker-compose up -d

infra-down: ## ├── Остановить инфраструктуру
	cd infra && docker-compose down

infra-logs: ## ├── Показать логи Kafka
	docker logs -f kafka_broker

infra-clean: ## └── Удалить инфраструктуру с volumes
	cd infra && docker-compose down -v --remove-orphans

# ========================================
# AUTH SERVICE
# ========================================
auth: ## 🔐 Auth Service
	@echo "Доступные команды для Auth сервиса:"
	@echo "  make auth-up     - Запустить сервис"
	@echo "  make auth-down   - Остановить сервис"
	@echo "  make auth-logs   - Показать логи"
	@echo "  make auth-build  - Пересобрать и запустить"
	@echo "  make auth-clean  - Удалить контейнеры и volumes"

auth-up: ## ├── Запустить Auth сервис
	cd auth_api && docker-compose up -d

auth-down: ## ├── Остановить Auth сервис
	cd auth_api && docker-compose down

auth-logs: ## ├── Показать логи Auth сервиса
	docker logs -f auth_api

auth-build: ## ├── Пересобрать и запустить Auth сервис
	cd auth_api && docker-compose up --build -d

auth-clean: ## └── Удалить Auth контейнеры и volumes
	cd auth_api && docker-compose down -v --remove-orphans

# ========================================
# BILLING SERVICE
# ========================================
billing: ## 💳 Billing Service
	@echo "Доступные команды для Billing сервиса:"
	@echo "  make billing-up     - Запустить сервис"
	@echo "  make billing-down   - Остановить сервис"
	@echo "  make billing-logs   - Показать логи"
	@echo "  make billing-build  - Пересобрать и запустить"
	@echo "  make billing-clean  - Удалить контейнеры и volumes"

billing-up: ## ├── Запустить Billing сервис
	cd billing_api && docker-compose up -d

billing-down: ## ├── Остановить Billing сервис
	cd billing_api && docker-compose down

billing-logs: ## ├── Показать логи Billing сервиса
	docker logs -f billing_api

billing-build: ## ├── Пересобрать и запустить Billing сервис
	cd billing_api && docker-compose up --build -d

billing-clean: ## └── Удалить Billing контейнеры и volumes
	cd billing_api && docker-compose down -v --remove-orphans

# ========================================
# PAYMENT SERVICE
# ========================================
payment: ## 💰 Payment Service
	@echo "Доступные команды для Payment сервиса:"
	@echo "  make payment-up     - Запустить сервис"
	@echo "  make payment-down   - Остановить сервис"
	@echo "  make payment-logs   - Показать логи"
	@echo "  make payment-build  - Пересобрать и запустить"
	@echo "  make payment-clean  - Удалить контейнеры и volumes"

payment-up: ## ├── Запустить Payment сервис
	cd payment_api && docker-compose up -d

payment-down: ## ├── Остановить Payment сервис
	cd payment_api && docker-compose down

payment-logs: ## ├── Показать логи Payment сервиса
	docker logs -f payment_api

payment-build: ## ├── Пересобрать и запустить Payment сервис
	cd payment_api && docker-compose up --build -d

payment-clean: ## └── Удалить Payment контейнеры и volumes
	cd payment_api && docker-compose down -v --remove-orphans

# ========================================
# ADMIN PANEL
# ========================================
admin: ## 🛠️ Admin Panel
	@echo "Доступные команды для Admin панели:"
	@echo "  make admin-up     - Запустить админку"
	@echo "  make admin-down   - Остановить админку"
	@echo "  make admin-logs   - Показать логи"
	@echo "  make admin-build  - Пересобрать и запустить"
	@echo "  make admin-clean  - Удалить контейнеры и volumes"

admin-up: ## ├── Запустить Admin панель
	cd admin_pannel && docker-compose up -d

admin-down: ## ├── Остановить Admin панель
	cd admin_pannel && docker-compose down

admin-logs: ## ├── Показать логи Admin панели
	docker logs -f admin_panel

admin-build: ## ├── Пересобрать и запустить Admin панель
	cd admin_pannel && docker-compose up --build -d

admin-clean: ## └── Удалить Admin контейнеры и volumes
	cd admin_pannel && docker-compose down -v --remove-orphans

# ========================================
# ALL SERVICES
# ========================================
all-up: ## 🚀 Запустить все сервисы (infra + auth + billing + payment + admin)
	@echo "Запуск инфраструктуры..."
	cd infra && docker-compose up -d
	@echo "Ожидание готовности Kafka..."
	@timeout 10 > nul
	@echo "Запуск сервисов..."
	cd auth_api && docker-compose up -d
	cd billing_api && docker-compose up -d
	cd payment_api && docker-compose up -d
	cd admin_pannel && docker-compose up -d
	@echo "✅ Все сервисы запущены!"
	@echo "Auth API: http://localhost:8000"
	@echo "Billing API: http://localhost:8001"
	@echo "Payment API: http://localhost:8002"
	@echo "Admin Panel (direct): http://localhost:8003"
	@echo "Admin Panel (nginx): http://localhost:8015"
	@echo "Kafka UI: http://localhost:8080"

all-down: ## 🛑 Остановить все сервисы
	cd auth_api && docker-compose down
	cd billing_api && docker-compose down
	cd payment_api && docker-compose down
	cd admin_pannel && docker-compose down
	cd infra && docker-compose down
	@echo "✅ Все сервисы остановлены!"

