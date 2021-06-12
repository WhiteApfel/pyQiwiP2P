FROM python:slim
MAINTAINER WhiteApfel 'white@pfel.ru'
WORKDIR /app
COPY . .
RUN python3 -m pip install -r requirements.txt
CMD ["python", "p2proxy/start.py"]