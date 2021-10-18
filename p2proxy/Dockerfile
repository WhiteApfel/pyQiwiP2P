FROM python:slim
LABEL maintainer="WhiteApfel white@pfel.ru"
WORKDIR /app
COPY . .
RUN python3 -m pip install -r p2proxy/requirements.txt
CMD ["python", "p2proxy/start.py"]