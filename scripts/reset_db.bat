cd ..
del db.sqlite3
echo yes|manage.py collectstatic
manage.py migrate
manage.py shell --plain < scripts/init_db.py
manage.py shell --plain < scripts/debug_init_db.py
cd scripts