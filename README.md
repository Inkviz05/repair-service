# Repair Service Requests

Веб-сервис для приёма и обработки заявок в ремонтную службу.

## Стек

- Python 3.12+
- Django 5.1
- SQLite
- Docker Compose

## Быстрый запуск (предпочтительный вариант)

```bash
docker compose up --build
```

Приложение: `http://localhost:8000`

## Запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
mkdir -p data
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Тестовые пользователи

- Диспетчер:
  - username: `dispatcher1`
  - password: `dispatcher123`
- Мастер 1:
  - username: `master1`
  - password: `master123`
- Мастер 2:
  - username: `master2`
  - password: `master123`

## Обязательные страницы

- `/requests/new/` — создание заявки
- `/dispatcher/` — панель диспетчера
- `/master/` — панель мастера

## Проверка гонки (take в работу)

### Вариант 1: два терминала (curl)

1. Войти под `master1` в браузере.
2. В двух терминалах одновременно отправить `POST` на:
   - `/master/requests/<ID>/take/`
3. Ожидаемое поведение:
   - один запрос успешный (редирект `302`)
   - второй получает `409 Conflict`

### Вариант 2: скрипт

```bash
chmod +x race_test.sh
./race_test.sh <REQUEST_ID>
```

Ожидаем в выводе пару кодов, где один `302`, второй `409`.

## Автотесты

```bash
python manage.py test
```

Покрыто:

- создание заявки со статусом `new`
- назначение и отмена заявок диспетчером
- конфликт при повторном `take` (`409`)
- завершение только из `in_progress`

## Структура

- `requests_app/models.py` — доменные модели `Request`, `RequestEvent`
- `requests_app/services.py` — бизнес-логика переходов статусов
- `requests_app/views.py` — страницы и действия
- `requests_app/management/commands/seed_data.py` — сиды
- `requests_app/tests.py` — автотесты

## Что включено по артефактам ТЗ

- Исходники приложения
- Миграции
- Сиды
- README
- DECISIONS.md
- PROMPTS.md
- 4 автотеста (требовалось минимум 2)

## Скриншоты

Для сдачи приложите 3 скриншота:

- страница создания заявки
- панель диспетчера
- панель мастера
