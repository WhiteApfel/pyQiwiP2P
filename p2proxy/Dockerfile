FROM python:3.9-slim
LABEL maintainer="WhiteApfel white@pfel.ru"
WORKDIR /app
COPY . .
RUN python3 -m pip install --no-cache-dir -r p2proxy/requirements.txt
CMD ["python", "p2proxy/app.py"]
