FROM python:3.12

WORKDIR /pricep

RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    && apt-get clean

COPY requirements.txt /pricep/

RUN pip install -r requirements.txt

RUN pip install playwright && playwright install --with-deps

COPY . /pricep/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
