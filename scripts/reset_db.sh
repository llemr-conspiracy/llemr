rm db.sqlite3
echo "yes" | python manage.py collectstatic
if python manage.py migrate; then
    python manage.py shell --plain < scripts/init_db.py
    python manage.py shell --plain < scripts/debug_init_db.py
    chmod g+rxw db.sqlite3
fi
