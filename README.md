# **Тендер Хак Москва: Реализация ИИ-ассистента для анализа поисковых запросов пользователей в режиме чата**

Проект разработан в рамках хакатона для Портала Поставщиков и представляет собой веб-инструмент на базе RAG-системы, обеспечивающий точные ответы на пользовательские запросы в реальном времени на основе загруженной базы знаний. Он решает проблему сложной навигации по инструкциям, предлагая интеллектуального помощника с поддержкой голосового ввода, перевода и прогнозирования вопросов.

---

# 2. Установка и запуск проекта

ML
```bash
git clone https://github.com/ItamMigel/TenderHack.git
cd TenderHack

# Установка зависимостей
pip install -r requirements.txt

# Запуск проекта
python server.py
```
Остальные запуски проекта находятся в конкретных папках tender_rag-main, tenderai-back-main, tenderai-front-main

---

# 3. Основной функционал проекта

- Преобразование речи в текст в режиме реального времени через whisper large v3 turbo
- Автоматический перевод текста между языками через ALMA 7B
- Синтез речи из текста при помощи kokoroTTS и coqui-XTTSv2. Поддерживает 19 языков
- Модель ллм - опенсорснутая Yandex GPT 5 lite 8B 6 дневной давности. Через Docling и умное разбиение на чанки и достаем мета информацию. Hyde и Rag Fusion
- Энкодер в раг: deepvk - bge - m3 - SOTA энкодер
- Классы выявили при помощи эмпирики и 4 LLM(грок 3, гемини 2.5, гпт, клауде 3.7). Классификация при помощи TochkaAI-RuRopeBert-e5-base-2k
- Система рекомендаций на TochkaAI-RuRopeBert-e5-base-2k и в FAISS, далее по косинусной близости подбираем топ 3 подходящих запроса
- Автосоздание класса - можно добавить свой класс и потом дообучить своего кастомногл бога. Например класс запрещенной темы 
---

# 4. Технологии и инструменты

### DevOps и инфраструктура

[![Docker](https://img.shields.io/badge/Docker-3.8-2496ED.svg)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-3.8-2496ED.svg)](https://docs.docker.com/compose/)
[![Git](https://img.shields.io/badge/Git-2.x-F05032.svg)](https://git-scm.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-3.x-2088FF.svg)](https://github.com/features/actions)

### Мониторинг и логирование

[![Prometheus](https://img.shields.io/badge/Prometheus-2.x-E6522C.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-10.x-F46800.svg)](https://grafana.com/)
[![ELK Stack](https://img.shields.io/badge/ELK%20Stack-8.x-005571.svg)](https://www.elastic.co/what-is/elk-stack)

### Инструменты разработки

[![VS Code](https://img.shields.io/badge/VS%20Code-1.85-007ACC.svg)](https://code.visualstudio.com/)
[![Postman](https://img.shields.io/badge/Postman-10.x-FF6C37.svg)](https://www.postman.com/)
[![Swagger](https://img.shields.io/badge/Swagger-3.0-85EA2D.svg)](https://swagger.io/)

---

# 5. Команда проекта
- [Калинин Алексей](https://github.com/ItamMigel) - Разработка ML-моделей
- Быков Вадим - дизайн, презентация, питч
- [Сергеев Даниил](https://github.com/DaniilSergeev17) - Разработка ML-моделей
- [Малинин Данила](https://github.com/MALINAYAGODA) - Разработка ML-моделей
- [Валеев Артем](https://github.com/artik19129) - Фронтенд, Бэкенд

---

# 6. Архитектура и структура проекта

```
project-root/
│
├── tender_rag-main - все, что относится к RAG
├── tenderai-back-main - все, что относится к бэкенду
├── tenderai-front-main - все, что относится к фронту
├── README.md - описание проекта
├── requirements.txt - зависимости
├── server.py - запуск основного скрипта
├── transcription_server.py - сервис транскрибации
├── translation.py - ALMA 7B для перевода
├── prepare_for_summarization.py - суммаризация отрывков разговора
├── api.py - апи сервисов
├── easyocr.py - скрипт OCR для документов
├── download_and_initialize_model.py - скачивание модели STT
├── initialize_tts.py - инициализация TTS
├── baseline_tts_with_if.py - скрипт TTS
├── baseline_pipeline.py - работа STT
├── mock_server.py - моковый сервис
├── recommend.py - сервис рекомендации
├── translation_api - апи для перевода 
├── translation.py - скрипт перевода
└── download_model.py - скачивание моделей
```
---

# 7. Демонстрация работы проекта



[Ссылка на скринкаст](https://drive.google.com/drive/folders/14tOxABlJqHAFomjVzVJjN1Yqsbqaber8?hl=ru)

---

# 8. Финальный текст-заключение

Проект представляет собой мощный интеллектуальный помощник для Портала Поставщиков, способный оперативно обрабатывать запросы пользователей на основе корпоративной базы знаний с использованием современной RAG-архитектуры и SOTA-компонентов. Он выделяется среди аналогов за счёт сочетания высокоточной системы поиска (HyDE + Rag Fusion), голосовых интерфейсов, поддержки мультиязычности, прогноза запросов и возможности добавления пользовательских классов и дообучения модели.

В будущем планируется дообучение модели с помощью RLHF для повышения удовлетворённости ответами, развитие механизма автосоздания новых классов, а также расширение рекомендаций с учётом пользовательского поведения. Устойчивость к ошибкам благодаря RAG Fusion делает систему надёжной и готовой к масштабному внедрению.
---

# 9. Лицензия

Этот проект распространяется под лицензией MIT.
