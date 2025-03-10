# Используем облегченную версию Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /pricep

# Устанавливаем системные зависимости для Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libxkbcommon0 libasound2 \
    && rm -rf /var/lib/apt/lists/*  # Удаляем кеш APT

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt /pricep/
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Playwright и его зависимости
RUN pip install --no-cache-dir playwright && playwright install --with-deps

# Копируем весь проект в контейнер
COPY . /pricep/

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
