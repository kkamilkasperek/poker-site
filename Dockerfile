FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "Poker.asgi:application"]