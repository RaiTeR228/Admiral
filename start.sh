#!/bin/bash
# при первом запуске сразу запускать генерацию токена

# добавить функцию одного токена для каждого плагина


requirements_file="req.txt"

python3 -m venv venv &
pid=$!

while kill -0 $pid 2>/dev/null; do
    for s in '[|]' '[/]' '[-]' '[\]'; do
        printf "\r%s Создание venv... " "$s"
        sleep 0.1
    done
done
printf "\r[+]Создание venv... Готово!   \n"

echo "Активация виртуального окружения..."
source venv/bin/activate

echo "Установка зависимостей..."
pip3 install --upgrade pip
pip3 install django djangorestframework psycopg django-cors-headers django-filter
pip install -r "$requirements_file"
clear

echo "Создание токена для сервера..."
python3 main.py generate-token

echo "Запуск приложения..."
python3 main.py run