FROM python:2.7-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y git

RUN useradd -ms /bin/bash -r -U  -d /home/gunicorn_user gunicorn_user
RUN chown -R gunicorn_user /home/gunicorn_user
USER gunicorn_user

COPY . /home/gunicorn_user/osler
WORKDIR /home/gunicorn_user/osler
ENV PATH="${PATH}:/home/gunicorn_user/.local/bin"

RUN pip install --user --trusted-host pypi.python.org gunicorn
RUN pip install --user --trusted-host pypi.python.org psycopg2-binary
RUN pip install --user --trusted-host pypi.python.org -r requirements.txt
RUN pip install --user --trusted-host pypi.python.org django-debug-toolbar==1.9.1

EXPOSE 8000

CMD ["gunicorn", "--chdir", "osler", "--bind", "0.0.0.0:8000", "osler.gunicorn_wsgi:application", "--log-file", "-"]
