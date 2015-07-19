SETTINGS="--settings clintools.deploy_settings"

python manage.py collectstatic $SETTINGS
python manage.py makemigrations pttrack $SETTINGS && python manage.py migrate $SETTINGS