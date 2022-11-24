# Продуктовый помощник
![foodgram workflow](https://github.com/RiteHist/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание

Сайт для создания и просмотра рецептов. После регистрации пользователь имеет возможность создавать рецепты, используя предустановленный список ингредиентов и тегов, просматривать рецепты других пользователей и добавлять их в избранное и в список покупок. Пользователь также имеет возможность подписаться на заинтересовавшего его автора. Список покупок также можно скачать в виде списка ингредиентов в формате .txt. На главной странице и в списке избранного можно фильтровать рецепты по тегам.

## Стек технологий

- Python 3.9
- Nginx
- Docker
- PostgreSQL
- Django
- React
- Django REST Framework

## Запуск проекта
### Локально

Для запуска проекта локально нужно:

1. Установить git: https://git-scm.com/downloads
2. Установить Docker (https://www.docker.com/) и Docker Compose (https://docs.docker.com/compose/install/)
3. Клонировать данный репозиторий:
```
git clone git@github.com:RiteHist/foodgram-project-react.git
```
4. Перейти в каталог `/infra/` внутри клонированного репозитория
5. В файле `nginx.conf` в строке `server_name` ввести:
```
server_name 127.0.0.1;
```
6. Создать и заполнить файл `.env` в этом же каталоге на основе примера из файла `.env.example`
7. Из каталога `/infra/` запустить docker-compose:
```
docker-compose up -d --build
```
8. После запуска контейнеров, создать миграции в контейнере `backend`:
```
docker-compose exec -T backend python manage.py makemigrations
```
9. Запустить миграции:
```
docker-compose exec -T backend python manage.py migrate
```
10. Собрать статику:
```
docker-compose exec -T backend python manage.py collectstatic
```
11. Загрузить в базу списки ингредиентов и тегов:
```
docker-compose exec -T backend python manage.py add_ingredients
```
```
docker-compose exec -T backend python manage.py add_tags
```
12. Создать суперпользователя:
```
docker-compose exec -T backend python manage.py createsuperuser
```
### Запуск на удаленном сервере

Для запуска проекта на удаленном сервере:

1. Установить Docker (https://www.docker.com/) и Docker Compose (https://docs.docker.com/compose/install/)
2. Скопировать файлы `nginx.conf` и `docker-compose.yaml` из каталога `/infra/` на удаленный сервер
3. В файле `nginx.conf` в строке `server_name` ввести адрес удаленного сервера
4. Запусть docker-compose

Далее запуск проекта идентичен запуску локально начиная с пункта 8.

## Список важных эндпоинтов

- `/` - Главная страница сайта
- `/api/docs` - Документация API
- `/admin` - Панель администратора Django
