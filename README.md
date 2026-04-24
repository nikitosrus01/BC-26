<div align="left">

# Большие вызовы 2026 <img src="bv/static/gok.png" width="60">

<div align="center">
  
[![GitHub stars](https://img.shields.io/github/stars/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![GitHub forks](https://img.shields.io/github/forks/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![GitHub issues](https://img.shields.io/github/issues/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/issues)
[![License](https://img.shields.io/github/license/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/blob/main/LICENSE)

<br>

<img src="bv/repo/banner.jpeg">

<br>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Agisoft Metashape](https://img.shields.io/badge/Metashape-2.2.2-orange.svg)](https://www.agisoft.com/)
[![Ultralytics YOLO](https://img.shields.io/badge/YOLOv8-yellow.svg)](https://ultralytics.com/)

</div>

<div align="left">

## 🚀 Быстрый старт (2 минуты)

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
```

🌐 **http://localhost:5000** — готово!

---

<div align="center">

## ✨ Возможности

| Этап | Инструмент | Результат |
|------|------------|-----------|
| **1. Фотограмметрия** | Metashape 2.2.2 Pro | Ортомозаика 0.02м/пикс |
| **2. Детекция дефектов** | YOLOv8 | Трещины + координаты |
| **3. Экспорт** | JPG + JSON | Готовые данные |

**Время: 5-45 мин | ОЗУ: 8-20 ГБ**

</div>

<div align="center">

## 📱 Демо

<img src="https://via.placeholder.com/800x400/e2e8f0/1e293b?text=%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B0+ZIP" width="32%">
<img src="https://via.placeholder.com/800x400/10b981/ffffff?text=%D0%9E%D1%80%D1%82%D0%BE%D0%BC%D0%BE%D0%B7%D0%B0%D0%B8%D0%BA%D0%B0" width="32%">
<img src="https://via.placeholder.com/800x400/ef4444/ffffff?text=YOLO+%D0%A2%D1%80%D0%B5%D1%89%D0%B8%D0%BD%D1%8B" width="32%">

</div>

<div align="center">

## 🛠 Требования

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| **Metashape** | Pro 2.2.2 | Лицензия обязательна |
| **Python** | 3.8+ | `pip install -r requirements.txt` |
| **YOLO** | v8n | `best.pt` в корне |
| **GPU** | Intel Arc+ | CUDA необязательно |

</div>

<div align="center">

## 🚀 Производительность

```mermaid
graph TD
    A[10 фото] -->|5 мин| B[8 ГБ ОЗУ]
    C[27 фото] -->|15 мин| D[12 ГБ ОЗУ] 
    E[100 фото] -->|45 мин| F[20 ГБ ОЗУ]
```

</div>

<div align="center">

## 🔧 Частые проблемы

| ❌ Ошибка | ✅ Решение |
|----------|------------|
| `Folder not found` | `mkdir test_folder` + JPG |
| `License error` | Лицензия Metashape Pro |
| `CUDA out of memory` | `RESIZE_TO=2000` |
| `NameError: np` | `pip install numpy` |

</div>

---

## 📂 Структура проекта
```
BC-26/
├── app.py # Flask бэкенд + YOLO
├── metashape_ortho.py # Фотограмметрия Metashape
├── best.pt # Модель трещин
├── requirements.txt # Зависимости
├── templates/index.html # Веб-интерфейс
├── static/ # CSS/JS
└── test_folder/ # Тестовые фото
```


## ⚙️ Конфигурация

### app.py
```python
MODEL_PATH = "best.pt"              # Путь к YOLO
RESIZE_TO = 4000                    # Макс размер (пиксели)
ORTHOPHOTO_RESOLUTION = 0.02        # Разрешение (м/пикс)
CONFIDENCE = 0.25                   # Порог детекции
```

### metashape_ortho.py
downscale=2 # Среднее качество
HighAccuracy # Точное выравнивание
MildFiltering # Сглаживание шума
MosaicBlending # Смешивание текстур


## Использование

1. **Загрузите ZIP** с фото дрона (до 2 ГБ)
2. **Дождитесь** обработки (5-45 минут)
3. **Скачайте**:
   - `output.jpg` — ортомозаика
   - `annotated.jpg` — с разметкой трещин
   - `defects.json` — координаты дефектов

## API
POST /upload # ZIP + обработка
GET /health # Статус системы


## 📈 Результаты

**Вход**: ZIP с 27 фото  
**Выход**:
output.jpg # Ортомозаика
annotated.jpg # + Разметка трещин
defects.json # Координаты + confidence



## 👥 Автор

**Никита Голубицкий**  
[nikitosrus01@github](https://github.com/nikitosrus01)  
Челябинск, 2026

<div align="center">

## 📄 Лицензия

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)



**⭐ Поставьте звезду**  
**🐛 Баги → Issues**  
**💬 Вопросы → Discussions**

</div>