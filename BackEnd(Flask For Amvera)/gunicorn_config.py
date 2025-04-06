# Gunicorn configuration file
import multiprocessing

# Количество воркеров
workers = multiprocessing.cpu_count() * 2 + 1

# Таймауты
timeout = 300  # Увеличиваем таймаут до 5 минут
graceful_timeout = 120  # Увеличиваем graceful_timeout до 2 минут
keepalive = 5

# Настройки логирования
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Настройки воркеров
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Настройки SSL
keyfile = None
certfile = None

# Настройки привязки
bind = "0.0.0.0:8080"

# Настройки процесса
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Настройки перезапуска
reload = False
reload_extra_files = []
reload_engine = "auto"

# Настройки буферизации
buffer_size = 8192
