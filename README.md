<div align="center">

# BC-26

<div align="center">
  
[![GitHub stars](https://img.shields.io/github/stars/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![GitHub forks](https://img.shields.io/github/forks/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![GitHub issues](https://img.shields.io/github/issues/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/issues)
[![License](https://img.shields.io/github/license/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/blob/main/LICENSE)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Agisoft Metashape](https://img.shields.io/badge/Metashape-2.2.2-orange.svg)](https://www.agisoft.com/)
[![Ultralytics YOLO](https://img.shields.io/badge/YOLOv8-yellow.svg)](https://ultralytics.com/)

</div>

</div>

## Быстрый старт (2 минуты)

```bash
# 1. Установка
pip install -r requirements.txt

# 2. Тест фотограмметрии
mkdir test_folder
# Положите 3+ JPG/PNG в test_folder
"C:\Program Files\Agisoft\Metashape Pro\metashape.exe" -r metashape_ortho.py test_folder output.jpg
# Ожидаемый: SUCCESS: output.jpg

# 3. Запуск сервера
python app.py
http://localhost:5000 — готово.

<div align="center">
Возможности
Этап	Инструмент	Результат
1. Фотограмметрия	Metashape 2.2.2 Pro	Ортомозаика 0.02 м/пикс
2. Детекция дефектов	YOLOv8	Трещины + координаты
3. Экспорт	JPG + JSON	Готовые данные
Время: 5–45 мин | ОЗУ: 8–20 ГБ

</div><div align="center">
Демо
Загрузка ZIP	Ортомозаика	Детекция трещин
(интерфейс)	(результат)	(разметка)
</div><div align="center">
Требования
Компонент	Версия	Примечание
Metashape	Pro 2.2.2	Лицензия обязательна
Python	3.8+	pip install -r requirements.txt
YOLO	v8n	best.pt в корне
GPU	Intel Arc+	CUDA необязательно
</div>
Структура проекта
text
BC-26/
├── app.py               # Flask бэкенд + YOLO
├── metashape_ortho.py   # Фотограмметрия Metashape
├── best.pt              # Модель трещин
├── requirements.txt     # Зависимости
├── templates/
│   └── index.html       # Веб-интерфейс
├── static/              # CSS/JS
└── test_folder/         # Тестовые фото
Конфигурация
app.py
python
MODEL_PATH = "best.pt"              # Путь к YOLO
RESIZE_TO = 4000                    # Макс размер (пиксели)
ORTHOPHOTO_RESOLUTION = 0.02        # Разрешение (м/пикс)
CONFIDENCE = 0.25                   # Порог детекции
metashape_ortho.py
text
downscale=2           # Среднее качество
HighAccuracy          # Точное выравнивание
MildFiltering         # Сглаживание шума
MosaicBlending        # Смешивание текстур
<div align="center">
Производительность
Количество фото	Время	ОЗУ
10	5 мин	8 ГБ
27	15 мин	12 ГБ
100	45 мин	20 ГБ
</div>
Использование
Загрузите ZIP с фото дрона (до 2 ГБ)

Дождитесь обработки (5–45 минут)

Скачайте:

output.jpg — ортомозаика

annotated.jpg — с разметкой трещин

defects.json — координаты дефектов

<div align="center">
Частые проблемы
Ошибка	Решение
Folder not found	mkdir test_folder + положите JPG
License error	Проверьте лицензию Metashape Pro
CUDA out of memory	Уменьшите RESIZE_TO=2000
NameError: np	pip install numpy
</div>
API
text
POST /upload    # ZIP + обработка
GET /health     # Статус системы
Результаты
Вход: ZIP с 27 фото
Выход:

output.jpg — ортомозаика

annotated.jpg — разметка трещин

defects.json — координаты + confidence

Автор
Никита Голубицкий
https://github.com/nikitosrus01
Челябинск, 2026

Лицензия
MIT License