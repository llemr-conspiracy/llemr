FROM python:3.7-buster

RUN apt-get update && apt-get upgrade -y && \
	apt-get install -y git

COPY . /home/gunicorn_user/osler
WORKDIR /home/gunicorn_user/osler

RUN pip install --upgrade pip --trusted-host pypi.python.org
RUN pip install --trusted-host pypi.python.org -r requirements-prod.txt

EXPOSE 8000

CMD ["gunicorn", "--chdir", "osler", "--bind", "0.0.0.0:8000", \
     "osler.gunicorn_wsgi:application", "--log-file", "-", "--log-level", "debug"]
