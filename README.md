# CloudCLI
🚀 High-performance, asynchronous CLI Music Player powered by Python, VLC engine, and yt-dlp. Stream any track directly from the cloud with zero latency and smart buffering.
# 𝖒𝖎𝖓𝖓𝖆𝖗>_< CloudCLI Music Engine v4.0 🎧

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![VLC](https://img.shields.io/badge/Engine-VLC%2064--bit-orange?style=for-the-badge&logo=vlc-mediaplayer)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**CloudCLI Music Engine** — это мощный терминальный аудио-плеер, который превращает твою консоль в полноценную стриминговую станцию. Никаких скачиваний, никаких лишних GUI — только чистый звук и быстрый поиск.

## ✨ Особенности
- **Стриминг в реальном времени**: Мгновенное воспроизведение аудио напрямую с YouTube без временных файлов.
- **Smart Buffering**: Продвинутое сетевое кэширование (5000мс) для стабильной работы под VPN или при нестабильном соединении.
- **Асинхронное ядро**: Поиск и подгрузка треков происходят в фоновых потоках, не блокируя интерфейс.
- **Интеллектуальный UI**: Стилизованный терминальный интерфейс на базе `prompt_toolkit` с поддержкой "безопасного вывода" (сообщения не разрывают строку ввода).
- **VLC Backend**: Использование профессионального движка VLC для поддержки любых аудио-кодеков.
- **Защита от конфликтов**: Встроенная система `Safe Logging` предотвращает ошибки доступа к системным потокам вывода.

## 🛠 Технологический стек
- **Язык**: Python 3.10+
- **Движок**: VLC Media Player (через `python-vlc`)
- **Провайдер данных**: `yt-dlp`
- **Интерфейс**: `prompt_toolkit`

## 🚀 Быстрый старт

### Предварительные требования
1. Установите **VLC Media Player (64-bit)**. Это критически важно для работы аудио-движка.
   - [Скачать VLC](https://www.videolan.org/vlc/)
2. Убедитесь, что у вас установлен менеджер пакетов `uv` (рекомендуется) или `pip`.

### Установка
```bash
# Клонируйте репозиторий
git clone [https://github.com/silovskijmark601-rgb/cloud-cli-music.git](https://github.com/silovskijmark601-rgb/cloud-cli-music.git)
cd cloud-cli-music

# Установите зависимости
uv add python-vlc yt-dlp prompt-toolkit
# ИЛИ через pip:
# pip install python-vlc yt-dlp prompt-toolkit
