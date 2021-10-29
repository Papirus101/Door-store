# Проект находится в разработке
# Заказ дверей

Для установки установите все зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
Устновить свои данные для базы данных postgres в файле .env
```
DB_NAME=SET_YOU_NAME
DB_USER=SET_YOU_USER_NAME
DB_PASS=SET_YOU_PASSWORD
DB_HOST=SET_YOU_HOST
DB_PORT=SET_YOU_PORT
```
После чего произвести первоначальную настройку проекта
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Готово.