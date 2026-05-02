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
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024

MODEL_PATH = "C:/Users/user/Documents/GitHub/BC-2026/bv/best.pt"
METASHAPE_EXE = r"C:\Program Files\Agisoft\Metashape Pro\metashape.exe"
SCRIPT_METASHAPE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metashape_stitch.py")
CONFIDENCE = 0.25

if not os.path.exists(METASHAPE_EXE):
    raise RuntimeError(f"Metashape.exe не найден: {METASHAPE_EXE}")

print("Metashape:", METASHAPE_EXE)
print("Скрипт:", SCRIPT_METASHAPE)
print("Загрузка YOLO...")
model = YOLO(MODEL_PATH)
print("YOLO загружен")

jobs = {}
jobs_lock = threading.Lock()

# ------------------------------------------------------------
def detect_cold_zones(img_bgr):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    lower_blue = np.array([80, 25, 25])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    lower_cyan = np.array([70, 30, 80])
    upper_cyan = np.array([90, 255, 255])
    mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
    
    lower_light = np.array([85, 10, 150])
    upper_light = np.array([120, 100, 255])
    mask_light = cv2.inRange(hsv, lower_light, upper_light)
    
    mask = cv2.bitwise_or(mask_blue, mask_cyan)
    mask = cv2.bitwise_or(mask, mask_light)
    
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_bgr.copy()
    cold_count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 150:   
            cold_count += 1
            cv2.drawContours(result, [cnt], -1, (0, 0, 255), 3)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.putText(result, "Cold zone", (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
    return result, cold_count

def encode_image_to_base64(img_bgr, quality=98):
    _, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buffer).decode('utf-8')

def send_event(job_id, event_type, data):
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job['queue'].put({'type': event_type, 'data': data})

# ------------------------------------------------------------
def process_single_image_for_cracks(image_bytes, original_name):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Не удалось декодировать {original_name}")
    results = model(img, conf=CONFIDENCE)
    annotated = results[0].plot()
    count = len(results[0].boxes) if results[0].boxes else 0
    b64 = encode_image_to_base64(annotated)
    return b64, count

def process_images_thread(job_id, file_data, mode):
    try:
        print(f"=== Старт задачи {job_id[:8]}, режим {mode}, файлов: {len(file_data)} ===")
        send_event(job_id, 'log', f'Начало обработки, режим {mode}, файлов: {len(file_data)}')

        if mode == 'cracks':
            if len(file_data) == 1:
                send_event(job_id, 'log', 'Одно фото – анализ без сшивки')
                send_event(job_id, 'progress', {'step': 0, 'total': 1, 'desc': 'Анализ YOLO'})
                b64, count = process_single_image_for_cracks(file_data[0][1], file_data[0][0])
                send_event(job_id, 'log', f'🔍 Обнаружено трещин: {count}')
                result = {'panorama': b64, 'annotated': b64, 'has_panorama': False}
                send_event(job_id, 'result', result)
                return

            send_event(job_id, 'progress', {'step': 0, 'total': 5, 'desc': 'Загрузка изображений'})
            with tempfile.TemporaryDirectory() as tmpdir:
                input_folder = os.path.join(tmpdir, "input")
                os.makedirs(input_folder, exist_ok=True)
                image_paths = []
                for i, (original_name, data_bytes) in enumerate(file_data):
                    dst_path = os.path.join(input_folder, f"img_{i:03d}.jpg")
                    img = cv2.imdecode(np.frombuffer(data_bytes, np.uint8), cv2.IMREAD_COLOR)
                    if img is None:
                        raise ValueError(f"Не удалось декодировать {original_name}")
                    cv2.imwrite(dst_path, img, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    image_paths.append(dst_path)
                    send_event(job_id, 'log', f'Сохранён {original_name}')
                send_event(job_id, 'log', f'📸 Всего сохранено: {len(image_paths)}')
                send_event(job_id, 'progress', {'step': 1, 'total': 5, 'desc': 'Запуск Metashape'})

                ortho_jpg = os.path.join(tmpdir, "orthophoto.jpg")
                cmd = [METASHAPE_EXE, "-r", SCRIPT_METASHAPE, input_folder, ortho_jpg]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           text=True, cwd=tmpdir)
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        print(f"[Metashape] {line}")
                        send_event(job_id, 'log', f'[Metashape] {line}')
                        if "Aligning" in line:
                            send_event(job_id, 'progress', {'step': 1, 'total': 4, 'desc': 'Выравнивание...'})
                        elif "Building model" in line:
                            send_event(job_id, 'progress', {'step': 2, 'total': 4, 'desc': 'Построение модели...'})
                        elif "Orthomosaic" in line:
                            send_event(job_id, 'progress', {'step': 3, 'total': 4, 'desc': 'Ортомозаика...'})
                        elif "Exporting" in line:
                            send_event(job_id, 'progress', {'step': 4, 'total': 4, 'desc': 'Экспорт...'})
                rc = process.wait()
                if rc != 0 or not os.path.exists(ortho_jpg):
                    send_event(job_id, 'error', f'Metashape ошибка (код {rc})')
                    return

                send_event(job_id, 'log', 'Metashape успешен')
                send_event(job_id, 'progress', {'step': 5, 'total': 5, 'desc': 'YOLO анализ'})

                pano = cv2.imread(ortho_jpg)
                if pano is None:
                    send_event(job_id, 'error', 'Не удалось прочитать ортофотоплан')
                    return

                results = model(pano, conf=CONFIDENCE)
                annotated = results[0].plot()
                count = len(results[0].boxes) if results[0].boxes else 0
                send_event(job_id, 'log', f'🔍 Обнаружено трещин: {count}')

                pano_b64 = encode_image_to_base64(pano)
                annotated_b64 = encode_image_to_base64(annotated)
                result = {'panorama': pano_b64, 'annotated': annotated_b64, 'has_panorama': True}
                send_event(job_id, 'result', result)

        else:  # mode == 'thermal'
            send_event(job_id, 'log', 'Режим тепловых аномалий: обработка каждого кадра')
            all_annotated = []
            total = len(file_data)
            if total == 0:
                send_event(job_id, 'error', 'Нет загруженных изображений')
                return

            for idx, (original_name, data_bytes) in enumerate(file_data):
                img = cv2.imdecode(np.frombuffer(data_bytes, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    send_event(job_id, 'log', f'Не удалось декодировать {original_name}, пропускаем')
                    continue
                annotated, cold_count = detect_cold_zones(img)
                b64 = encode_image_to_base64(annotated)
                all_annotated.append(b64)
                send_event(job_id, 'log', f'Обработан {original_name} (холодных зон: {cold_count})')
                send_event(job_id, 'progress', {'step': idx+1, 'total': total, 'desc': f'Обработка {idx+1}/{total}'})

            if not all_annotated:
                send_event(job_id, 'error', 'Не удалось обработать ни одного изображения')
                return

            first_b64 = all_annotated[0]
            result = {
                'panorama': first_b64,
                'annotated': first_b64,
                'all_annotated': all_annotated,
                'has_panorama': False
            }
            send_event(job_id, 'log', f'Обработано {len(all_annotated)} изображений')
            send_event(job_id, 'result', result)

    except Exception as e:
        tb = traceback.format_exc()
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}\n{tb}")
        send_event(job_id, 'error', str(e))
    finally:
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id]['status'] = 'done'

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
    mode = request.form.get('mode', 'cracks')
    print(f"📥 Получен запрос: {len(files)} файлов, режим {mode}")

    if len(files) == 0:
        return jsonify({'error': 'Загрузите хотя бы одно изображение'}), 400

    file_data = [(f.filename, f.read()) for f in files]
    job_id = str(uuid.uuid4())
    q = queue.Queue()
    with jobs_lock:
        jobs[job_id] = {'queue': q, 'status': 'processing'}
    thread = threading.Thread(target=process_images_thread, args=(job_id, file_data, mode), daemon=True)
    thread.start()
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