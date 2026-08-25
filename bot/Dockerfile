FROM python:3.10-slim
WORKDIR /app

# Отключаем буферизацию логов Python, чтобы видеть сообщения в консоли Докера сразу, без задержек
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем твой главный файл бота (убедись, что он называется main.py или bot.py)
CMD ["python", "main.py"]
