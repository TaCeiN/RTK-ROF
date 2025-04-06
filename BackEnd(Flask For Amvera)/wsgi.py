import logging
import sys
import os
from pathlib import Path
from app import app

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info('Starting application...')

# Определяем базовую директорию
BASE_DIR = Path(__file__).resolve().parent

# Создаем папку uploads если её нет
uploads_dir = BASE_DIR / 'uploads'
uploads_dir.mkdir(exist_ok=True)

# Создаем папку static если её нет
static_dir = BASE_DIR / 'static'
static_dir.mkdir(exist_ok=True)

# Настраиваем приложение
app.config['UPLOAD_FOLDER'] = str(uploads_dir)
app.config['STATIC_FOLDER'] = str(static_dir)

if __name__ == "__main__":
    logger.info('Running development server...')
    app.run()
