FROM python:2.7-slim

# ENV PYTHONUNBUFFERED 1
# ENV DATABASE_PASSWORD debug-password
# ENV DATABASE_NAME osler
# ENV DATABASE_USER django
# ENV DATABASE_PORT 5432
# ENV DATABASE_HOST db

RUN apt-get update && apt-get upgrade -y && apt-get install -y git

WORKDIR /osler

COPY . /osler

RUN pip install --trusted-host pypi.python.org gunicorn
RUN pip install --trusted-host pypi.python.org psycopg2-binary
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install --trusted-host pypi.python.org django-debug-toolbar==1.9.1

RUN python osler/manage.py collectstatic --noinput
RUN python -c "import string,random; uni=string.ascii_letters+string.digits+string.punctuation; print repr(''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))]))" > /osler/osler/secrets/secret_key.txt

# RUN python osler/manage.py check --settings osler.docker_settings
# RUN python osler/manage.py migrate --settings osler.docker_settings

EXPOSE 8000

CMD ["gunicorn", "--chdir", "osler", "--bind", "0.0.0.0:8000", "osler.gunicorn_wsgi:application", "--log-file", "-"]
# CMD ["python", "osler/manage.py", "runserver", "--settings", "osler.docker_settings", "0.0.0.0:8000"]
