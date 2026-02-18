FROM python:3.11-slim

# робоча папка
WORKDIR /app

# копіюємо файли
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# запуск
CMD ["python", "main.py"]
