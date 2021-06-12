FROM python:slim
MAINTAINER WhiteApfel 'white@pfel.ru'
WORKDIR /app
COPY p2proxy/requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY p2proxy .
CMD [ "python", "start.py"]