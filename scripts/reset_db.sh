rm db.sqlite3
rm pttrack/migrations/000*py
python manage.py collectstatic
python manage.py makemigrations pttrack && python manage.py migrate && python manage.py shell < init_db.py
