FROM python:3.10-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Открываем порт 8080 для Django-панели предиктора
EXPOSE 8080

# Промышленная команда запуска Django-сервера на порту 8080 внутри контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
