# Проект Foodgram

## Описание
<p>
Foodgram — это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и формировать список покупок для выбранных блюд.

Основные возможности:

   * Неавторизованный пользователь может:
     - просматривать рецепты на главной странице
     - просматривать отдельные страницы рецептов
     - просматривать страницы пользователей
     - зарегистрироваться
   * Авторизованный пользователь может:
     - создавать, редактировать, удалять рецепты
     - подписываться на других авторов рецептов
     - добавлять в избранное рецепты других авторов
     - добавлять рецепты других авторов себе в корзину
     - скачать файл с ингредиентами и их количеством, добавленных в корзину рецептов
     - получить короткую ссылку на рецепт
     - установить, удалить собственный аватар
</p>
<p>
  Настроен запуск проекта в контейнерах Docker. Настроено автоматическое тестирование и деплой этого проекта на удалённый сервер с обновлением образов на DockerHub при помощи сервиса GitHub Actions. Также написан подробный файл README по развороту проекта.
</p>

### Технологии
Python 3.9, Django 3.2, djangorestframework 3.12, gunicorn 20.1, Nginx 1.18, PostgreSQL, Docker

## Техническое описание
В проекте Foodgram есть две версии:
- Обычная версия используется, чтобы развернуть проект на своём компьютере. В ней образы контейнеров создаются в процессе разворота проекта.
- Продакшн-версия используется, чтобы развернуть проект на удаленном сервере. В ней используются готовые образы контейнеров с dockerhub.
- Проект доступен по адресу - [http://recipebook.sytes.net/](http://recipebook.sytes.net/)
- Статус последнего workflow: ![workflow status](https://github.com/VanZep/Foodgram/actions/workflows/main.yml/badge.svg)
---
### Инструкция запуска проекта на своём компьютере
#### 1. Установите Docker, если его нет:
**для Windows**

- *Сначала установите Windows Subsystem for Linux по [инструкции с официального сайта Microsoft](https://learn.microsoft.com/ru-ru/windows/wsl/install).*
- *Зайдите на [официальный сайт](https://www.docker.com/products/docker-desktop/), скачайте и установите Docker Desktop.*

**для Linux**

- *Скачайте и установите curl — консольную утилиту, которая умеет скачивать файлы по команде пользователя:*
```
sudo apt update
sudo apt install curl
```
- *С помощью утилиты curl скачайте скрипт для установки докера с официального сайта:*
```
curl -fSL https://get.docker.com -o get-docker.sh
```
- *Запустите сохранённый скрипт с правами суперпользователя:*
```
sudo sh ./get-docker.sh
```
- *Дополнительно к Docker установите утилиту Docker Compose:*
```
sudo apt install docker-compose-plugin
```
- *Проверьте, что Docker работает:*
```
sudo systemctl status docker
```

**для macOS**

- *Зайдите на [официальный сайт](https://www.docker.com/products/docker-desktop/) и скачайте установочный файл Docker Desktop для вашей платформы — Apple Chip для процессоров M1/M2 и Intel Chip для процессоров Intel.*
- *Откройте скачанный DMG-файл и перетащите Docker в Applications, а потом — запустите программу Docker.*

#### 2. Склонируйте проект себе на компьютер:
- *В терминале выполните команду из той директории, в которой хотите разместить проект:*
```
git clone git@github.com:VanZep/Foodgram.git
```
- *Перейдите в корневую директорию проекта:*
```
cd Foodgram
```
#### 3. В корневой директории проекта создайте файл .env:
```
touch .env
```
#### 4. Наполните его данными по аналогии с файлом .env.example:
```
nano .env
```
```
POSTGRES_DB=название_бд
POSTGRES_USER=юзернейм_бд
POSTGRES_PASSWORD=пароль_бд
DB_NAME=имя_бд
DB_HOST=хост_бд (название контейнера БД)
DB_PORT=порт_бд
SECRET_KEY=секретный_ключ_джанго
DEBUG=флаг_отладки (True или False)
ALLOWED_HOSTS=адрес1,адрес2,домен1
```
#### 5. Разверните проект на своём компьютере:
- *В терминале, из директории Foodgram, выполните команду:*
```
docker compose up
```
- *В новом окне терминала выполните следующие команды, не меняя указанный порядок:*
```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /static/static/
docker compose exec backend cp -r /app/test_media/. /media/
```
- *Можете наполнить базу проекта тестовыми данными:*
```
docker compose exec backend python manage.py load_json
docker compose exec backend python manage.py load_csv
```
- *Можете создать пользователя superuser, чтобы войти на сайт:*
```
docker compose exec backend python manage.py createsuperuser
```

- **Теперь можете войти на сайт, как пользователь, которого создали.**

#### Проект будет доступен по адресу - [http://localhost:7000/](http://localhost:7000/)
---
### Инструкция запуска проекта на удалённом сервере
#### 1. Выполните 2-ой пункт из инструкции запуска проекта на своём компьютере
#### 2. Подключитесь к серверу, выполнив команду в терминале:
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_закрытого_SSH-ключа username@server_ip
```
#### 3. Поочерёдно выполните на сервере команды для установки Docker и Docker Compose для Linux:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```
#### 4. Из корневой папки проекта Foodgram на своём компьютере скопируйте файл .env в корневую папку проекта foodgram на удалённом сервере. Для этого можно воспользоваться командой в терминале, например:
```
scp -i путь_до_файла_с_SSH_ключом/название_файла_закрытого_SSH-ключа .env \
  username@server_ip:/home/username/foodgram/.env
```
#### 5. Также скопируйте файл docker-compose.production.yml:
```
scp -i путь_до_файла_с_SSH_ключом/название_файла_закрытого_SSH-ключа docker-compose.production.yml \
  username@server_ip:/home/username/foodgram/docker-compose.production.yml
```
#### 6. Установите Nginx на удалённом сервере, выполнив команду из любой директории:
```
sudo apt install nginx -y
```
#### 7. Настройте Nginx:
- *Через редактор Nano откройте файл конфигурации Nginx:*
```
sudo nano /etc/nginx/sites-enabled/default
```
- *Удалите все настройки из файла, запишите и сохраните новые:*
```
server {

    listen 80;
    server_name публичный_ip_вашего_удалённого_сервера или домен;
    
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:7000;
    }

}
```
- *Запустите Nginx командой:*
```
sudo systemctl start nginx
```
#### 8. Из корневой папки проекта foodgram запустите Docker Compose в режиме демона командой:
```
sudo docker compose -f docker-compose.production.yml up -d
```
#### 9. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /static/static/, выполнив поочереди команды:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/test_media/. /media/
```
- *Можете наполнить базу проекта тестовыми данными:*
```
docker compose -f docker-compose.production.yml exec backend python manage.py load_json
docker compose -f docker-compose.production.yml exec backend python manage.py load_csv
```
- *Можете создать пользователя superuser, чтобы войти на сайт:*
```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
- *Теперь можете войти на сайт, как пользователь, которого создали.*
#### Проект будет доступен по адресу - ***публичный_ip_вашего_удалённого_сервера или домен***

### Автор:
***VanZep***
