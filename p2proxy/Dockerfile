FROM python:slim
MAINTAINER WhiteApfel 'white@pfel.ru'
WORKDIR /app
COPY p2proxy/ .
RUN python3 -m pip install -r requirements.txt
CMD ["python", "start.py"]