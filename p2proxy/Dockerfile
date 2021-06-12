FROM python:slim
MAINTAINER WhiteApfel 'white@pfel.ru'
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY .p2proxy .
CMD [ "python", "start.py"]