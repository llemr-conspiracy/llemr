SETTINGS="--settings clintools.deploy_settings"

python manage.py collectstatic $SETTINGS
python manage.py makemigrations core $SETTINGS && python manage.py migrate $SETTINGS
