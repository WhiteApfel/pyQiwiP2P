FROM python:slim
MAINTAINER WhiteApfel 'white@pfel.ru'
WORKDIR /
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY . .
CMD [ "python", "start.py"]