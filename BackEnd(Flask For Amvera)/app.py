import os
import logging
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import requests
import json
import urllib3
from requests.exceptions import RequestException
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from flask_cors import CORS

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))

CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

app.config['UPLOAD_FOLDER'] = str(BASE_DIR / 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'nikolay.krutykh.sss@gmail.com'
app.config['MAIL_PASSWORD'] = 'gcgjqwptqfnwbsxq'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logger.info('Application configured')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_TOKEN = "eyJhbGciOiJIUzM4NCJ9.eyJzY29wZXMiOlsid2hpc3BlciJdLCJzdWIiOiJoazciLCJpYXQiOjE3NDI0NzkwODcsImV4cCI6MjYwNjM5MjY4N30.ILwdQ9z5gt4SusCZssm6oGg6kBSyY5IGuveVO81QKkksVBCDtHlzYlgHuLDf3P6n"
OPENROUTER_API_KEY = "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"

MODELS = [
    "openrouter/quasar-alpha",
    "openrouter/mistral-7b-instruct",
    "openrouter/llama-2-70b-chat",
    "openrouter/anthropic/claude-3-opus",
    "openrouter/anthropic/claude-3-sonnet"
]

def summarize_text(text: str, instruction: str) -> str:
    if not text or not instruction:
        logger.error("Пустой текст или инструкция для summarize_text")
        return "Ошибка: Пустой текст или инструкция"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"{instruction}\n\n{text}"
    
    optimized_models = [
        "openrouter/mistral-7b-instruct",
        "openrouter/quasar-alpha",
        "openrouter/anthropic/claude-3-sonnet",
        "openrouter/llama-2-70b-chat",
        "openrouter/anthropic/claude-3-opus"
    ]
    
    session = requests.Session()
    session.verify = True
    
    session.timeout = (60, 180)
    
    for model in optimized_models:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10000
        }
        
        try:
            logger.info(f"Попытка подключения к OpenRouter API с моделью {model}")
            
            if model in ["openrouter/mistral-7b-instruct", "openrouter/quasar-alpha"]:
                timeout = (30, 90)
            else:
                timeout = (60, 180)
                
            response = session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"].strip()
                if content:
                    logger.info(f"Успешное получение ответа от модели {model}")
                    return content
                else:
                    logger.warning(f"Получен пустой ответ от модели {model}")
            elif "error" in result:
                logger.warning(f"Ошибка от API для модели {model}: {result.get('error')}")
            else:
                logger.warning(f"Неверный формат ответа от API для модели {model}")
                
        except requests.exceptions.SSLError as e:
            logger.error(f"Ошибка SSL при подключении к API с моделью {model}: {str(e)}")
        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при подключении к API с моделью {model}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Ошибка подключения к API с моделью {model}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API с моделью {model}: {str(e)}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к API с моделью {model}: {str(e)}")
    
    proxy_list = [
        {
            "http": "http://FJnRFN:o3wguh@94.131.54.28:9058",
            "https": "http://FJnRFN:o3wguh@94.131.54.28:9058"
        },
        {
            "http": "http://FJnRFN:o3wguh@94.131.54.28:9059",
            "https": "http://FJnRFN:o3wguh@94.131.54.28:9059"
        }
    ]

    for model in optimized_models[:2]:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10000
        }
        
        for proxies in proxy_list:
            try:
                logger.info(f"Попытка подключения к OpenRouter API с моделью {model} и прокси")
                
                session.proxies = proxies
                response = session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=(30, 90)
                )
                response.raise_for_status()
                
                result = response.json()
                if "choices" in result and result["choices"]:
                    content = result["choices"][0]["message"]["content"].strip()
                    if content:
                        logger.info(f"Успешное получение ответа от модели {model} через прокси")
                        return content
                    else:
                        logger.warning(f"Получен пустой ответ от модели {model} через прокси")
                elif "error" in result:
                    logger.warning(f"Ошибка от API для модели {model}: {result.get('error')}")
                    break
                else:
                    logger.warning(f"Неверный формат ответа от API для модели {model}")
                    break
                    
            except requests.exceptions.Timeout:
                logger.error(f"Таймаут при подключении к API с моделью {model} через прокси")
                continue
            except requests.exceptions.ConnectionError:
                logger.error(f"Ошибка подключения к API с моделью {model} через прокси")
                continue
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при запросе к API с моделью {model} и прокси: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе к API с моделью {model}: {str(e)}")
                continue
    
    logger.error("Не удалось получить ответ ни от одной модели")
    return "Ошибка: Не удалось получить ответ ни от одной модели. Пожалуйста, попробуйте позже."

def transcribe_via_api(file_path: str) -> str:
    url = "https://ai.rt.ru/api/1.0/whisper/audio"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }
    
    request_payload = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "audio": {
            "model": "whisper-fast",
            "task": "trans",
            "sigm_tr": 1,
            "prompt": "это разговор оператора с клиентом",
            "vad_filter": True,
            "rnoise": True
        }
    }

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return "Ошибка: Файл не найден"

    try:
        file_size = os.path.getsize(file_path)
        if file_size > 25 * 1024 * 1024:
            logger.warning(f"Файл слишком большой: {file_size} байт")
            return "Ошибка: Файл слишком большой. Максимальный размер - 25MB."
    except Exception as e:
        logger.error(f"Ошибка при проверке размера файла: {str(e)}")
        return "Ошибка: Не удалось проверить размер файла"

    try:
        logger.info("Попытка прямого подключения к API транскрипции")
        
        with open(file_path, "rb") as f:
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_type = "audio/mpeg"
            if file_ext == ".wav":
                mime_type = "audio/wav"
            elif file_ext == ".ogg":
                mime_type = "audio/ogg"
            elif file_ext == ".flac":
                mime_type = "audio/flac"
            
            files = {
                "request": (None, json.dumps(request_payload), "application/json"),
                "file": (os.path.basename(file_path), f, mime_type)
            }
            
            result = direct_api_request(url, headers, files=files)
            if result and isinstance(result, list) and len(result) > 0:
                transcript = result[0].get('message', {}).get('content', '')
                if transcript:
                    logger.info("Успешное получение транскрипции через прямое подключение")
                    return transcript.strip()
                else:
                    logger.warning("Получен пустой ответ от API при прямом подключении")
            else:
                logger.warning("Неверный формат ответа от API при прямом подключении")
    except Exception as e:
        logger.error(f"Ошибка при прямом подключении к API транскрипции: {str(e)}")
    
    proxy_list = [
        None,
        {
            "http": "http://FJnRFN:o3wguh@94.131.54.28:9058",
            "https": "http://FJnRFN:o3wguh@94.131.54.28:9058"
        },
        {
            "http": "http://FJnRFN:o3wguh@94.131.54.28:9059",
            "https": "http://FJnRFN:o3wguh@94.131.54.28:9059"
        }
    ]

    for proxies in proxy_list:
        try:
            logger.info(f"Попытка подключения к API с прокси: {proxies}")
            
            with open(file_path, "rb") as f:
                file_ext = os.path.splitext(file_path)[1].lower()
                mime_type = "audio/mpeg"
                if file_ext == ".wav":
                    mime_type = "audio/wav"
                elif file_ext == ".ogg":
                    mime_type = "audio/ogg"
                elif file_ext == ".flac":
                    mime_type = "audio/flac"
                
                files = {
                    "request": (None, json.dumps(request_payload), "application/json"),
                    "file": (os.path.basename(file_path), f, mime_type)
                }
                
                session = requests.Session()
                session.verify = False
                if proxies:
                    session.proxies = proxies
                
                response = session.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    timeout=60
                )
                
                response.raise_for_status()
                
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    transcript = result[0].get('message', {}).get('content', '')
                    if transcript:
                        logger.info("Успешное получение транскрипции через прокси")
                        return transcript.strip()
                    else:
                        logger.warning("Получен пустой ответ от API при использовании прокси")
                        continue
                else:
                    logger.warning(f"Неверный формат ответа от API при использовании прокси: {result}")
                    continue
                
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return f"Ошибка: Файл {file_path} не найден"
        except RequestException as e:
            logger.error(f"Ошибка при запросе к API с прокси {proxies}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к API: {str(e)}")
            continue
    
    logger.error("Все попытки подключения к API Whisper не удались")
    return "Ошибка: Не удалось подключиться к API Whisper после всех попыток. Пожалуйста, попробуйте позже."

def process_audio(file_path, num_speakers, speakers_names):
    try:
        logger.info("Начало транскрипции аудио через Whisper API")
        raw_text = transcribe_via_api(file_path)
        
        if not raw_text:
            logger.error("Получен пустой результат от Whisper API")
            return None, "Ошибка: Не удалось распознать речь. Возможно, файл поврежден или содержит неразборчивую речь."
        
        if raw_text.startswith("Ошибка"):
            logger.error(f"Ошибка при транскрипции: {raw_text}")
            return None, raw_text

        logger.info("Начало форматирования диалога")
        try:
            formatted_dialogue = summarize_text(raw_text, (
                f"Отформатируй следующий текст как диалог между {', '.join(speakers_names)}. "
                f"Распредели реплики между {', '.join(speakers_names)}, не добавляя новых слов, "
                "и не исправляй текст. Сохрани содержание диалога в исходном виде, только пометь кто говорит что."
            ))
            
            if formatted_dialogue.startswith("Ошибка"):
                logger.error(f"Ошибка при форматировании диалога: {formatted_dialogue}")
                return None, formatted_dialogue
                
        except Exception as e:
            logger.error(f"Исключение при форматировании диалога: {str(e)}")
            return None, f"Ошибка при форматировании диалога: {str(e)}"

        logger.info("Начало создания итогового конспекта")
        try:
            final_summary = summarize_text(formatted_dialogue, (
                "На основе этого диалога оформи текст в виде краткого пересказа встречи. "
                "Выдели обязательства с фиксацией ответственных и сроков выполнения"
                "В формате Заголовок: Содержание"
            ))
            
            if final_summary.startswith("Ошибка"):
                logger.error(f"Ошибка при создании конспекта: {final_summary}")
                return {
                    'raw_text': raw_text,
                    'formatted_dialogue': formatted_dialogue,
                    'final_summary': "Не удалось создать итоговый конспект. Пожалуйста, попробуйте позже."
                }, None
                
        except Exception as e:
            logger.error(f"Исключение при создании конспекта: {str(e)}")
            return {
                'raw_text': raw_text,
                'formatted_dialogue': formatted_dialogue,
                'final_summary': f"Ошибка при создании конспекта: {str(e)}"
            }, None

        logger.info("Успешное завершение обработки аудио")
        return {
            'raw_text': raw_text,
            'formatted_dialogue': formatted_dialogue,
            'final_summary': final_summary
        }, None

    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке аудио: {str(e)}")
        return None, f"Ошибка при обработке аудио: {str(e)}"

def send_email(recipient_email, results):
    if not recipient_email or not results:
        logger.error("Отсутствуют необходимые данные для отправки email")
        return False, "Отсутствуют необходимые данные для отправки email"

    try:
        logger.info(f"Подготовка email для отправки на {recipient_email}")
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = recipient_email
        msg['Subject'] = 'Результаты транскрипции аудио'

        body = f"""
        <html>
        <body>
            <h2>Результаты транскрипции аудио</h2>
            
            <h3>Распознанный текст:</h3>
            <pre>{results['raw_text']}</pre>
            
            <h3>Отформатированный диалог:</h3>
            <pre>{results['formatted_dialogue']}</pre>
            
            <h3>Итоговый конспект:</h3>
            <pre>{results['final_summary']}</pre>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        try:
            logger.info("Подключение к SMTP серверу")
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            logger.info("Отправка email")
            server.send_message(msg)
            server.quit()
            
            logger.info("Email успешно отправлен")
            return True, "Email успешно отправлен"
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Ошибка аутентификации SMTP сервера")
            return False, "Ошибка аутентификации SMTP сервера"
        except smtplib.SMTPException as e:
            logger.error(f"Ошибка SMTP при отправке email: {str(e)}")
            return False, f"Ошибка SMTP при отправке email: {str(e)}"
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке email: {str(e)}")
            return False, f"Неожиданная ошибка при отправке email: {str(e)}"
            
    except Exception as e:
        logger.error(f"Ошибка при подготовке email: {str(e)}")
        return False, f"Ошибка при подготовке email: {str(e)}"

def direct_api_request(url, headers, files=None, json_data=None, timeout=60):
    try:
        logger.info(f"Попытка прямого подключения к API: {url}")
        
        session = requests.Session()
        session.verify = False
        
        try:
            if files:
                response = session.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    timeout=timeout
                )
            elif json_data:
                response = session.post(
                    url, 
                    headers=headers, 
                    json=json_data, 
                    timeout=timeout
                )
            else:
                response = session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            if not result:
                logger.warning("Получен пустой ответ от API")
                return None
                
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Таймаут при подключении к API")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка подключения к API")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка при подключении к API: {str(e)}")
            return None
        except json.JSONDecodeError:
            logger.error("Ошибка декодирования JSON ответа от API")
            return None
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при прямом подключении к API: {str(e)}")
        return None

@app.route('/')
def index():
    logger.debug('Serving index page')
    try:
        template_path = os.path.join(app.template_folder, 'index.html')
        logger.debug(f"Путь к шаблону: {template_path}")
        
        if not os.path.exists(template_path):
            logger.error(f"Шаблон не найден: {template_path}")
            return "Ошибка: Шаблон index.html не найден", 500
            
        static_folder = app.static_folder
        if not os.path.exists(static_folder):
            logger.warning(f"Папка статических файлов не найдена: {static_folder}")
            os.makedirs(static_folder, exist_ok=True)
            logger.info(f"Создана папка статических файлов: {static_folder}")
            
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            logger.warning(f"Папка для загрузок не найдена: {upload_folder}")
            os.makedirs(upload_folder, exist_ok=True)
            logger.info(f"Создана папка для загрузок: {upload_folder}")
            
        logger.info("Успешная загрузка главной страницы")
        return render_template('index.html')
        
    except Exception as e:
        logger.error(f"Ошибка при отображении главной страницы: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Ошибка: {str(e)}", 500

@app.route('/health')
def health_check():
    try:
        logger.debug("Проверка работоспособности приложения")
        
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            logger.warning(f"Папка для загрузок не найдена: {upload_folder}")
            os.makedirs(upload_folder, exist_ok=True)
            logger.info(f"Создана папка для загрузок: {upload_folder}")
            
        template_folder = app.template_folder
        if not os.path.exists(template_folder):
            logger.warning(f"Папка шаблонов не найдена: {template_folder}")
            return jsonify({"status": "unhealthy", "error": "Папка шаблонов не найдена"}), 500
            
        static_folder = app.static_folder
        if not os.path.exists(static_folder):
            logger.warning(f"Папка статических файлов не найдена: {static_folder}")
            os.makedirs(static_folder, exist_ok=True)
            logger.info(f"Создана папка статических файлов: {static_folder}")
            
        logger.info("Приложение работает нормально")
        return jsonify({"status": "healthy"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка при проверке работоспособности: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.warning("Попытка загрузки без файла")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("Попытка загрузки пустого файла")
        return jsonify({'error': 'No selected file'}), 400

    allowed_extensions = {'mp3', 'wav', 'ogg', 'flac'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        logger.warning(f"Попытка загрузки файла с недопустимым расширением: {file_ext}")
        return jsonify({'error': f'Недопустимый формат файла. Разрешены только: {", ".join(allowed_extensions)}'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Сохранение файла: {filename}")
        file.save(file_path)

        num_speakers = int(request.form.get('num_speakers', 2))
        speakers_names = request.form.get('speakers_names', '').split(',')
        speakers_names = [name.strip() for name in speakers_names if name.strip()]

        if len(speakers_names) == 0 and num_speakers > 1:
            speakers_names = [f"Говорящий {i+1}" for i in range(num_speakers)]
        elif len(speakers_names) != num_speakers:
            logger.warning(f"Несоответствие количества имен ({len(speakers_names)}) и говорящих ({num_speakers})")
            return jsonify({'error': f'Указано {len(speakers_names)} имени, но должно быть {num_speakers}'}), 400

        logger.info(f"Начало обработки аудио файла: {filename}")
        try:
            result, error = process_audio(file_path, num_speakers, speakers_names)
        except Exception as e:
            logger.error(f"Исключение при обработке аудио: {str(e)}")
            try:
                os.remove(file_path)
                logger.info(f"Файл {filename} удален после ошибки")
            except Exception as cleanup_error:
                logger.error(f"Ошибка при удалении файла {filename}: {str(cleanup_error)}")
            
            return jsonify({'error': f'Ошибка при обработке аудио: {str(e)}'}), 500
        
        try:
            os.remove(file_path)
            logger.info(f"Файл {filename} успешно удален")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла {filename}: {str(e)}")

        if error:
            if "Не удалось подключиться к API Whisper" in error:
                logger.error("Ошибка подключения к API Whisper")
                return jsonify({'error': 'Не удалось подключиться к сервису распознавания речи. Пожалуйста, проверьте подключение к интернету и попробуйте позже.'}), 503
            elif "Файл слишком большой" in error:
                logger.warning(f"Попытка загрузки слишком большого файла: {filename}")
                return jsonify({'error': 'Файл слишком большой. Максимальный размер - 25MB.'}), 413
            else:
                logger.error(f"Ошибка при обработке файла {filename}: {error}")
                return jsonify({'error': error}), 400

        logger.info(f"Успешная обработка файла: {filename}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке файла: {str(e)}")
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Файл {filename} удален после ошибки")
        except Exception as cleanup_error:
            logger.error(f"Ошибка при удалении файла {filename}: {str(cleanup_error)}")
        
        return jsonify({'error': 'Произошла внутренняя ошибка сервера. Пожалуйста, попробуйте позже.'}), 500

@app.route('/send-email', methods=['POST'])
def send_results_email():
    try:
        logger.info("Получен запрос на отправку результатов по email")
        data = request.json
        
        if not data:
            logger.warning("Получен пустой JSON в запросе")
            return jsonify({'error': 'Отсутствуют данные в запросе'}), 400
            
        recipient_email = data.get('recipient_email')
        results = data.get('results')

        if not recipient_email:
            logger.warning("Отсутствует email получателя")
            return jsonify({'error': 'Отсутствует email получателя'}), 400
            
        if not results:
            logger.warning("Отсутствуют результаты для отправки")
            return jsonify({'error': 'Отсутствуют результаты для отправки'}), 400

        required_fields = ['raw_text', 'formatted_dialogue', 'final_summary']
        missing_fields = [field for field in required_fields if field not in results]
        if missing_fields:
            logger.warning(f"Отсутствуют обязательные поля в результатах: {', '.join(missing_fields)}")
            return jsonify({'error': f'Отсутствуют обязательные поля в результатах: {", ".join(missing_fields)}'}), 400

        logger.info(f"Отправка результатов на email: {recipient_email}")
        success, message = send_email(recipient_email, results)
        
        if success:
            logger.info("Результаты успешно отправлены по email")
            return jsonify({'message': message}), 200
        else:
            logger.error(f"Ошибка при отправке результатов по email: {message}")
            return jsonify({'error': message}), 500

    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON в запросе")
        return jsonify({'error': 'Неверный формат JSON в запросе'}), 400
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке запроса: {str(e)}")
        return jsonify({'error': f'Ошибка при обработке запроса: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 