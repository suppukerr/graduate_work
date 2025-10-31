from src.core.config import settings

# Количество воркеров (процессов), обрабатывающих запросы
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1

worker_class = settings.server.worker_class

# Какой хост и порт будет слушать Gunicorn
bind = f"{settings.server.host}:{settings.server.port}"

# Таймаут для обработки запроса (в секундах)
timeout = settings.server.timeout

# Очередь входящих запросов перед обработкой
backlog = settings.server.backlog

# Сколько запросов обработает воркер перед перезапуском
max_requests = settings.server.max_requests

# Разброс количества запросов до перезапуска воркера
# Если max_requests = 1000, то воркеры перезапустятся случайно после 950-1050 запросов
# Это предотвращает одновременный перезапуск всех воркеров
max_requests_jitter = settings.server.max_requests_jitter

# Логи каждого HTTP-запроса (GET, POST и т.д.)
accesslog = "-"  # вывод в stdout

# # Логи ошибок воркера
# errorlog = "-"   # вывод в stdout

# # Уровень логирования
# loglevel = "info"

# # --- новые строки для печати print() и перезагрузки при изменениях кода ---
# capture_output = True  # чтобы print() шел в stdout
# reload = True          # авто-перезагрузка при изменении кода