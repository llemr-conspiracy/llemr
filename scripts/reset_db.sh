rm db.sqlite3
rm pttrack/migrations/000*py
echo "yes" | python manage.py collectstatic
python manage.py makemigrations pttrack && python manage.py migrate && python manage.py shell < scripts/debug_init_db.py
