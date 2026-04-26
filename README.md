<div align="center">

# 🏔️ Большие вызовы 2026
**v2.2** • Обновлено **26.03.2026**  
*🔥 Скачивание OBJ 3D-моделей из веб-сервиса*

<img src="bv/static/gok.png" width="80">

[![Stars](https://img.shields.io/github/stars/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![Forks](https://img.shields.io/github/forks/nikitosrus01/BC-26?style=social)](https://github.com/nikitosrus01/BC-26)
[![Issues](https://img.shields.io/github/issues/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/issues)
[![License](https://img.shields.io/github/license/nikitosrus01/BC-26)](https://github.com/nikitosrus01/BC-26/blob/main/LICENSE)

<br>

<img src="bv/repo/banner.jpeg" alt="Баннер проекта">

<br>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Metashape](https://img.shields.io/badge/Metashape-2.2.2-orange.svg)](https://www.agisoft.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-yellow.svg)](https://ultralytics.com/)

</div>

## 📋 Что нового в v2.2 (26.03.2026)

<div align="center">

**🚀 Скачивание OBJ 3D-моделей прямо из браузера!**

**1. Результат работы — 3D модель карьера**  
<img src="repo/image1.png" alt="3D OBJ модель карьера" width="500">

**2. Кнопка Download в веб-интерфейсе**  
<img src="repo/image.png" alt="Кнопка OBJ download" width="400">

🔧 Стабильность + мобильная адаптация

</div>

## 📸 О проекте

**Автоматизированный мониторинг карьеров: фотограмметрия → YOLO трещины → OBJ 3D.**

Для конкурса «Большие вызовы 2026». Интерес **АО «Томинский ГОК»** — лидер добычи меди РФ.[web:1]

## ✨ Возможности

- **📐 Фотограмметрия** — Agisoft Metashape Pro
- **🧠 Детекция трещин** — YOLOv8 `best.pt`
- **🌐 Веб-сервис** — Flask + OBJ download ✨
- **💾 Экспорт** — JPG/PNG/OBJ

## 🎥 Демо веб-сервиса

<div align="center">

**Снимки → ортофотоплан → трещины → OBJ download**

<video width="800" controls loop>
  <source src="repo/demo.mp4" type="video/mp4">
  Ваш браузер не поддерживает видео.
</video>

*Реальные данные Томинского ГОК*

</div>

[image:24]

## 🧠 Технологии

| Компонент | Инструмент | Версия |
|-----------|------------|--------|
| Backend | Python/Flask | 3.8+ |
| Фото | Metashape Pro | 2.2.2 |
| AI | YOLOv8 | v8 |

## 🚀 Быстрый старт

1. **Клонировать + зависимости:**
```bash
git clone https://github.com/nikitosrus01/BC-26
cd BC-26
pip install -r requirements.txt
```

2. **Тест фотограмметрии:**
```bash
mkdir test_folder
# Добавь 3+ JPG/PNG
"C:\Program Files\Agisoft\Metashape Pro\metashape.exe" -r metashape_stitch.py test_folder output.jpg
```

3. **Запуск:**
```bash
python app.py
```
→ **http://localhost:5000**

## ⚙️ Конфигурация `app.py`

```python
MODEL_PATH = "best.pt"
RESIZE_TO = 4000
ORTHOPHOTO_RESOLUTION = 0.02
CONFIDENCE = 0.25
# v2.2:
OBJ_EXPORT = True
```

## 📊 Производительность

| Снимков | Время | RAM |
|---------|-------|-----|
| 10 | ~5 мин | 8 ГБ |
| 27 | ~15 мин | 12 ГБ |
| 100 | ~45 мин | 20 ГБ |

## 🗂️ Структура
```
BC-26/
├── app.py # Flask + OBJ v2.2
├── metashape_stitch.py
├── best.pt
├── repo/ # Твои файлы здесь!
│ ├── image1.png # 3D модель
│ ├── image.png # Кнопка
│ └── demo.mp4 # Видео
└── ...
```


## 🐛 Troubleshooting

| Ошибка | Решение |
|--------|---------|
| Folder not found | `mkdir test_folder` |
| License error | Активируй Metashape Pro |
| CUDA OOM | `RESIZE_TO=2000` |
| No NumPy | `pip install numpy` |

## 🎯 Заказчики

**Частные:** РМК (Томинский), Металлоинвест, УГМК  
**Публичные:** СУЭК, ФосАгро, Селигдар

## 📜 MIT License

## 👤 Никита Голубицкий
[GitHub](https://github.com/nikitosrus01) | Челябинск, 2026

⭐ **Звездуй!** 🐛 Issues | 💬 Discussions

<div align="center">
<img src="https://img.shields.io/badge/внедрение-ГОК-brightgreen">
</div>