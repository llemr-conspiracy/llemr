rm db.sqlite3
rm pttrack/migrations/000*py
echo "yes" | python manage.py collectstatic
if python manage.py makemigrations pttrack && python manage.py migrate; then
    python manage.py shell < scripts/init_db.py
    python manage.py shell < scripts/debug_init_db.py
fi
