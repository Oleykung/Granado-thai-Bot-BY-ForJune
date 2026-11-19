FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render / Railway จะใช้ PORT env
ENV KEEP_ALIVE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
