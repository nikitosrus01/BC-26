# BC-26: Фотограмметрия + Детекция дефектов

Автоматический пайплайн обработки дроновых снимков для строительного контроля.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Agisoft Metashape](https://img.shields.io/badge/Metashape-2.2.2-orange.svg)](https://www.agisoft.com/)
[![Ultralytics YOLO](https://img.shields.io/badge/YOLOv8-yellow.svg)](https://ultralytics.com/)

## Описание

BC-26 обрабатывает дроновые снимки в два этапа:

1. **Фотограмметрия** (Agisoft Metashape Pro 2.2.2) → создание ортомозаики
2. **Детекция дефектов YOLOv8** → поиск трещин на ортомозаике

Для инспекции карьеров, а также подоёдет для дорог, фасадов, крыш.

## Возможности

- Загрузка ZIP-архива (10-100+ фото, до 2 ГБ)
- Автоматическое создание ортомозаики (0.02 м/пиксель)
- Детекция трещин YOLOv8 (настраиваемый порог)
- Экспорт: ортомозаика + разметка + JSON координаты
- Без GUI Metashape (headless режим)

## Требования

### Программное обеспечение
Windows 10/11
Agisoft Metashape Pro 2.2.2 (лицензия обязательна)
Python 3.8+

text

### Оборудование
Процессор: Intel Core Ultra 5+ / AMD Ryzen 5+
ОЗУ: 16 ГБ+ (32 ГБ рекомендовано)
Видеокарта: Intel Arc / NVIDIA GTX 1650+
Диск: 50 ГБ свободного места

text

## Установка

```bash
pip install flask ultralytics opencv-python numpy
```

Скачайте `best.pt` (модель YOLOv8 для трещин) в корень проекта.

## Быстрый запуск

### 1. Проверка Metashape
```bash
mkdir test_folder
# Положите 3+ фото JPG/PNG в test_folder
"C:\Program Files\Agisoft\Metashape Pro\metashape.exe" -r metashape_ortho.py test_folder output.jpg
# Ожидаемый результат: SUCCESS: output.jpg
```

### 2. Запуск сервера
```bash
python app.py
```

Откройте: http://localhost:5000

## Структура проекта
BC-26/
├── app.py # Flask бэкенд + YOLO
├── metashape_ortho.py # Фотограмметрия Metashape
├── best.pt # Модель YOLOv8
├── templates/
│ └── index.html # Веб-интерфейс
├── static/ # CSS/JavaScript
└── test_folder/ # Тестовые фото

text

## Использование

1. Загрузите ZIP-архив с фото дрона
2. Дождитесь обработки (5-45 минут)
3. Скачайте результаты:
   - `output.jpg` — ортомозаика
   - `annotated.jpg` — ортомозаика с разметкой
   - `defects.json` — координаты дефектов

## Настройки

### app.py
```python
MODEL_PATH = "best.pt"              # Путь к модели YOLO
RESIZE_TO = 4000                    # Макс размер (пиксели)
ORTHOPHOTO_RESOLUTION = 0.02        # Разрешение (м/пикс)
CONFIDENCE = 0.25                   # Порог детекции
```

### metashape_ortho.py
downscale=2 # Среднее качество
HighAccuracy # Точное выравнивание
MildFiltering # Сглаживание шума
MosaicBlending # Смешивание текстур

text

## Производительность

| Фото | Время обработки | Пик ОЗУ |
|------|-----------------|---------|
| 10   | 5 минут         | 8 ГБ    |
| 27   | 15 минут        | 12 ГБ   |
| 100  | 45 минут        | 20 ГБ   |

## Устранение неисправностей

| Ошибка | Решение |
|--------|---------|
| `Folder not found` | Создайте `test_folder` с JPG/PNG |
| `Metashape.Chunk has no attribute` | Обновите `metashape_ortho.py` |
| `License error` | Проверьте лицензию Metashape Pro |
| `CUDA out of memory` | `RESIZE_TO=2000` |
| `NameError: np` | `pip install numpy` |

## API
POST /upload # Загрузка + обработка ZIP
GET /health # Статус системы

text

## Лицензия

MIT — разрешено коммерческое использование.

## Автор

Никита Голубицкий (nikitosrus01)

## Благодарности

- Agisoft Metashape Professional 2.2.2
- Ultralytics YOLOv8
- Flask Framework