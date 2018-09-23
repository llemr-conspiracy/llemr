FROM python:2.7-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y git

WORKDIR /osler

COPY . /osler

RUN pip install --trusted-host pypi.python.org gunicorn
RUN pip install --trusted-host pypi.python.org psycopg2-binary
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install --trusted-host pypi.python.org django-debug-toolbar==1.9.1

RUN python osler/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--chdir", "osler", "--bind", "0.0.0.0:8000", "osler.gunicorn_wsgi:application", "--log-file", "-", "--log-level", "DEBUG"]
