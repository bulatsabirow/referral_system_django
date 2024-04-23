# Referral System #

## Требования ##
1. [Python >= 3.10](https://www.python.org/downloads/)
2. [Poetry](https://pypi.org/project/poetry/)

## Описание API ##

- `auth/mobile` - принимает как входной параметр
номер телефона пользователя и отправляет на него код подтверждения.
- `auth/token` - принимает в качестве параметров номер телефона
пользователя и отправленный на него код подтверждения.
- `user` - при отправке GET-запроса возвращает
данные текущего пользователя, PATCH-запрос используется для активации
инвайт кода другого пользователя.

## Запуск проекта с помощью Docker ##
1. Запуск необходимых контейнеров:
    `
    docker compose -f 'deploy/docker-compose.yml' up -d 
    `

## Классический способ запуска проекта ##
1. Вход в виртуальное окружение:
    `
    poetry shell 
    `
2. Установка зависимостей:
    `
    poetry install
    `
3. Поднятие PostgreSQL с помощью Docker:
    `
    docker compose -f 'docker-compose.dev.yml' up -d
    `
4. Выполнение миграций:
    `
    python manage.py migrate
    `
5. Инициализация линтера:
    `
    pre-commit install
    `
6. Запуск сервера для разработки на http://localhost:8000:
    `
    python manage.py runserver
    `
