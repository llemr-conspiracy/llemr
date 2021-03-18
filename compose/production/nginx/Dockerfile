FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY certs/cert.key /etc/nginx/certs/cert.key 
COPY certs/cert.crt /etc/nginx/certs/cert.crt 