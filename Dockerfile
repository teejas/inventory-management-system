FROM ubuntu:18.04

LABEL maintainer="Tejas Siripurapu <tejas97siripruapu@gmail.com>"

RUN apt-get update && apt-get install -y python3 python3-pip git curl

WORKDIR /ims/
COPY . .
RUN ls && python3 -m pip install -r requirements.txt

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:8000 api.inventory:app
