# SPAS System API

## Описание

**SPAS System API** — REST API для проверки работы алгоритмов обнаружения аномалий 

### Технологии
- **Язык:** Python  
- **Фреймворк:** FastAPI  
- **Библиотеки:** Pydentic

---

## Запуск проекта

**Порт:** `8000`  
**URL:** `http://localhost:8000`


## Подготовка

Перед запуском удалите из названия файла .env.example часть .example

## Docker
**Для запуска в фоновом режиме, в корневой папке прописать:**
```bash
docker-compose up -d
```

**Для остановки, там же прописать:**
```bash
docker-compose down -v
``` 
[avalanche_detector.py](app%2Fsrc%2Fdetectors%2Favalanche_detector.py)
**Для запуска в консольном режиме, в корневой папке прописать:**
```bash
docker-compose up --build
```
**Для остановки нажать:** 
Ctrl+C + Ctrl+S

---

## Документация

После запуска, по этому адресу будет автоматически-генерируемая документация:

**URL:** `http://localhost:8000/docs`
