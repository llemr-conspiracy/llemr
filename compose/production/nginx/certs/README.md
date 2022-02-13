- To create a **selfsigned certificate** copy the following, run it in the terminal and follow the instructions. The cert-files are placed in the .config/nginx/certs folder.

  $ openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout ./compose/production/nginx/certs/cert.key -out ./compose/production/nginx/certs/cert.crt
