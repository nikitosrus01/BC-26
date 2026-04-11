import os
import cv2
import numpy as np
import tempfile
from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

MODEL_PATH = "C:/Users/user/Documents/GitHub/BC-2026/bv/best.pt"
CONFIDENCE = 0.25

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Модель не найдена: {MODEL_PATH}")

print("⏳ Загрузка модели YOLO...")
model = YOLO(MODEL_PATH)
print("✅ Модель загружена")

def encode_image_to_base64(img_bgr):
    _, buffer = cv2.imencode('.jpg', img_bgr)
    return base64.b64encode(buffer).decode('utf-8')

def detect_hot_zones(img_bgr, threshold_hue=(0, 30), threshold_saturation=(100, 255), threshold_value=(200, 255)):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, threshold_saturation[0], threshold_value[0]])
    upper_red1 = np.array([threshold_hue[1], threshold_saturation[1], threshold_value[1]])
    lower_red2 = np.array([170, threshold_saturation[0], threshold_value[0]])
    upper_red2 = np.array([180, threshold_saturation[1], threshold_value[1]])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img_bgr.copy()
    cv2.drawContours(result, contours, -1, (0, 0, 255), 3)
    for cnt in contours:
        if cv2.contourArea(cnt) > 200:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.putText(result, "Hot zone", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    return result, len(contours)

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
def process_images():
    files = request.files.getlist('images')
    if len(files) < 2:
        return jsonify({'error': 'Загрузите минимум 2 изображения'}), 400

    mode = request.form.get('mode', 'cracks')
    print(f"Режим: {mode}")

    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = []
        for f in files:
            if f.filename == '':
                continue
            path = os.path.join(tmpdir, f.filename)
            f.save(path)
            image_paths.append(path)

        images = []
        for p in image_paths:
            img = cv2.imread(p)
            if img is not None:
                images.append(img)

        if len(images) < 2:
            return jsonify({'error': 'Не удалось прочитать изображения'}), 400

        print("🖼️ Сшиваю панораму...")
        stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
        status, pano = stitcher.stitch(images)
        if status != cv2.Stitcher_OK:
            return jsonify({'error': 'Сшивка не удалась. Увеличьте перекрытие между кадрами.'}), 400
        print(f"✅ Панорама готова, размер: {pano.shape}")

        if mode == 'cracks':
            pano_rgb = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
            results = model(pano_rgb, conf=CONFIDENCE)
            annotated = results[0].plot()
            print(f"🔍 Найдено трещин: {len(results[0].boxes) if results[0].boxes else 0}")
        else:
            annotated, num_hot = detect_hot_zones(pano)
            print(f"🔥 Найдено горячих зон: {num_hot}")

        pano_b64 = encode_image_to_base64(pano)
        annotated_b64 = encode_image_to_base64(annotated)

        return jsonify({
            'panorama': pano_b64,
            'annotated': annotated_b64
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)