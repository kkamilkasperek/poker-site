# Poker Game - Django Application

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/poker-game.git
cd poker-game
```

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate

python manage.py runserver

## Environment Variables
See `.env.example` for required environment variables.
