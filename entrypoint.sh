python manage.py migrate
python manage.py collectstatic

gunicorn main.wsgi:application --bind 0.0.0.0:8000