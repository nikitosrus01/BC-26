import os
import sys
import tempfile
import subprocess
import base64
import cv2
import numpy as np
import uuid
import json
import queue
import threading
import traceback
from flask import Flask, render_template, request, jsonify, Response
from ultralytics import YOLO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024   # 2 ГБ

# ------------------------------------------------------------
# НАСТРОЙКИ
# ------------------------------------------------------------
MODEL_PATH = "C:/Users/user/Documents/GitHub/BC-2026/bv/best.pt"
METASHAPE_EXE = r"C:\Program Files\Agisoft\Metashape Pro\metashape.exe"
SCRIPT_METASHAPE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metashape_stitch.py")
CONFIDENCE = 0.25

if not os.path.exists(METASHAPE_EXE):
    raise RuntimeError(f"❌ Metashape.exe не найден: {METASHAPE_EXE}")

print("✅ Metashape:", METASHAPE_EXE)
print("✅ Скрипт:", SCRIPT_METASHAPE)
print("⏳ Загрузка YOLO...")
model = YOLO(MODEL_PATH)
print("✅ YOLO загружен")

# ------------------------------------------------------------
# ХРАНИЛИЩЕ ЗАДАЧ
# ------------------------------------------------------------
jobs = {}
jobs_lock = threading.Lock()

# ------------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ------------------------------------------------------------
def encode_image_to_base64(img_bgr, quality=98):
    _, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buffer).decode('utf-8')

def send_event(job_id, event_type, data):
    prefix = f"[SSE:{job_id[:8]}][{event_type}]"
    if event_type == 'log':
        print(f"{prefix} {data}")
    elif event_type == 'progress':
        print(f"{prefix} Шаг {data['step']}/{data['total']} – {data['desc']}")
    elif event_type == 'error':
        print(f"{prefix} ❌ ОШИБКА: {data}")
    elif event_type == 'result':
        print(f"{prefix} Результат готов")
    
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job['queue'].put({'type': event_type, 'data': data})

# ------------------------------------------------------------
# ОСНОВНАЯ ЛОГИКА (поток)
# ------------------------------------------------------------
def process_images_thread(job_id, file_data, mode):
    try:
        print(f"=== Старт задачи {job_id[:8]} ===")
        send_event(job_id, 'log', 'Начало обработки')
        send_event(job_id, 'progress', {'step': 0, 'total': 5, 'desc': 'Загрузка изображений'})

        with tempfile.TemporaryDirectory() as tmpdir:
            input_folder = os.path.join(tmpdir, "input")
            os.makedirs(input_folder, exist_ok=True)
            print(f"DEBUG: Временная папка {input_folder} создана")

            image_paths = []
            print(f"DEBUG: Начинаем сохранение {len(file_data)} файлов")
            for i, (original_name, data) in enumerate(file_data):
                dst_path = os.path.join(input_folder, f"img_{i:03d}.jpg")
                print(f"DEBUG: сохраняю {original_name} -> {dst_path}")
                try:
                    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                    if img is None:
                        raise ValueError(f"Не удалось декодировать {original_name}")
                    cv2.imwrite(dst_path, img, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    image_paths.append(dst_path)
                    print(f"DEBUG: сохранён {dst_path} ({img.shape[1]}x{img.shape[0]})")
                    send_event(job_id, 'log', f'Сохранён {dst_path} ({img.shape[1]}x{img.shape[0]})')
                except Exception as e:
                    print(f"ОШИБКА сохранения {original_name}: {e}")
                    send_event(job_id, 'error', f'Ошибка сохранения {original_name}: {str(e)}')
                    return

            if len(image_paths) < 2:
                send_event(job_id, 'error', 'Недостаточно изображений (минимум 2)')
                return

            print(f"DEBUG: Всего сохранено {len(image_paths)} изображений")
            send_event(job_id, 'log', f'📸 Всего сохранено: {len(image_paths)}')
            send_event(job_id, 'progress', {'step': 1, 'total': 5, 'desc': 'Запуск Metashape'})

            # Запуск Metashape
            ortho_jpg = os.path.join(tmpdir, "orthophoto.jpg")
            cmd = [METASHAPE_EXE, "-r", SCRIPT_METASHAPE, input_folder, ortho_jpg]
            print(f"Запуск Metashape: {' '.join(cmd)}")
            send_event(job_id, 'log', f'Запуск Metashape: {" ".join(cmd)}')

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=tmpdir
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"[Metashape] {line}")
                    send_event(job_id, 'log', f'[Metashape] {line}')
                    if "1/4 Aligning..." in line:
                        send_event(job_id, 'progress', {'step': 1, 'total': 4, 'desc': 'Выравнивание...'})
                    elif "2/4 Building" in line:
                        send_event(job_id, 'progress', {'step': 2, 'total': 4, 'desc': 'Построение глубины и модели...'})
                    elif "3/4 Orthomosaic..." in line:
                        send_event(job_id, 'progress', {'step': 3, 'total': 4, 'desc': 'Ортомозаика...'})
                    elif "4/4 Exporting..." in line:
                        send_event(job_id, 'progress', {'step': 4, 'total': 4, 'desc': 'Экспорт...'})

            process.wait()
            rc = process.returncode
            print(f"Metashape завершился с кодом {rc}")
            if rc != 0 or not os.path.exists(ortho_jpg):
                send_event(job_id, 'error', f'Metashape завершился с ошибкой (код {rc})')
                return

            send_event(job_id, 'log', '✅ Metashape успешно завершён')
            send_event(job_id, 'progress', {'step': 5, 'total': 5, 'desc': 'YOLO анализ'})

            pano = cv2.imread(ortho_jpg)
            if pano is None:
                send_event(job_id, 'error', 'Не удалось загрузить ортофотоплан')
                return

            if mode == 'cracks':
                print("Запуск YOLO анализа...")
                send_event(job_id, 'log', 'Поиск трещин (YOLO)...')
                results = model(pano, conf=CONFIDENCE)
                annotated = results[0].plot()
                count = len(results[0].boxes) if results[0].boxes else 0
                print(f"Обнаружено трещин: {count}")
                send_event(job_id, 'log', f'Обнаружено трещин: {count}')
            else:
                print("Режим thermal: отдаём панораму без анализа")
                send_event(job_id, 'log', 'Режим тепловизора – отдаём панораму')
                annotated = pano.copy()

            pano_b64 = encode_image_to_base64(pano)
            annotated_b64 = encode_image_to_base64(annotated)
            result = {'panorama': pano_b64, 'annotated': annotated_b64}
            send_event(job_id, 'result', result)
            send_event(job_id, 'log', 'Обработка завершена')
            print(f"=== Задача {job_id[:8]} успешно завершена ===")

    except Exception as e:
        tb = traceback.format_exc()
        print(f"КРИТИЧЕСКАЯ ОШИБКА в задаче {job_id[:8]}: {e}\n{tb}")
        send_event(job_id, 'error', f'{str(e)}\n{tb}')
    finally:
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id]['status'] = 'done' if 'result' in locals() else 'error'

# ------------------------------------------------------------
# МАРШРУТЫ
# ------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/instruction')
def instruction():
    return render_template('instruction.html')

@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/author')
def author():
    return render_template('author.html')

@app.route('/process', methods=['POST'])
def start_process():
    files = request.files.getlist('images')
    print(f"Получен запрос: {len(files)} файлов")
    if len(files) < 2:
        print("Ошибка: недостаточно файлов")
        return jsonify({'error': 'Минимум 2 изображения'}), 400

    mode = request.form.get('mode', 'cracks')
    print(f"Режим: {mode}")

    file_data = []
    for f in files:
        f.stream.seek(0)
        data = f.read()
        file_data.append((f.filename, data))
        print(f"Прочитан файл: {f.filename}, размер {len(data)} байт")

    job_id = str(uuid.uuid4())
    q = queue.Queue()
    with jobs_lock:
        jobs[job_id] = {'queue': q, 'status': 'processing'}

    thread = threading.Thread(
        target=process_images_thread,
        args=(job_id, file_data, mode),
        daemon=True
    )
    thread.start()
    print(f"Задача запущена, job_id = {job_id[:8]}")
    return jsonify({'job_id': job_id})

@app.route('/stream/<job_id>')
def stream(job_id):
    def event_stream():
        with jobs_lock:
            job = jobs.get(job_id)
        if not job:
            yield f"data: {json.dumps({'type': 'error', 'data': 'Неверный job_id'})}\n\n"
            return

        q = job['queue']
        while True:
            try:
                event = q.get(timeout=30)
                if event['type'] == 'result':
                    yield f"event: result\ndata: {json.dumps(event['data'])}\n\n"
                    break
                else:
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
            except queue.Empty:
                with jobs_lock:
                    status = job['status']
                if status != 'processing':
                    break
                yield ": heartbeat\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    print("Сервер запущен на http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)