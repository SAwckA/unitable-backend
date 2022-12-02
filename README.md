# Шаблон бэкенда на python fastapi

<hr>

### Запуск и сборка приложения в Docker compose
#### *Запуск Postgres в docker, как зависимость*

```shell
# Сборка приложение

$ sudo docker-compose build .
```

```shell
# Запуск приложения вместе с базой данных

$ sudo docker-compose up -d
```

```shell
# Завершение работы

$ sudo docker-compose down
```

### Запуск контейнера с удалённой бд и уже собранном образе на ghcr.io

```shell
# Запуск контейнера
```

> Документация к API станет доступна по адресу **0.0.0.0:8000/docs**
<hr>

### Переменные окружения

#### *.env*

```dotenv
# База данных postgres

DB_USER= # Имя пользователя
DB_NAME= # База данных
DB_PASS= # Пароль пользователя
DB_HOST= # Адресс БД
DB_PORT= # Порт БД

# Ключ для подписи JWT
SECRET_KEY=

# Конфигурация JWT
JWT_ALG=             # default: HS512
JWT_ACCESS_EXPIRE=   # default: 30 days
JWT_REFRESH_EXPIRE=  # default: 60 days
```

#### *Compose env* (*For copy*)
```yaml
environment:
  - DB_PASS=
  - DB_USER=
  - DB_HOST=
  - DB_NAME=
  - DB_PORT=

  - SECRET_KEY=
  - JWT_ALG=
  - JWT_ACCESS_EXPIRE=
  - JWT_REFRESH_EXPIRE=
```

<hr>

### Разработка

> :warning: Необходима тестовая база данных, можно запустить в docker-compose

#### *Makefile*

```shell
# Запуск проекта

$ make run
```

```shell
# Линт кода

$ make lint
```

```shell
# Pretty кода

$ make pretty
```

```shell
# Перед push
# Линт и pretty

$ make plint
```