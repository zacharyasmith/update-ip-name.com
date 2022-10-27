## -*- dockerfile-image-name: "localhost:5000/update-ip-name-com" -*-

FROM python:3.8-alpine

WORKDIR /runarea

COPY *.py /runarea/

CMD python3 update_dns_ip.py
