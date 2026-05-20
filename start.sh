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
pip install -r "$requirements_file"
clear
echo "Запуск приложения..."
python3 main.py run