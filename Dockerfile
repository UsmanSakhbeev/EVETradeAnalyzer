# Указываем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN uv venv

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Указываем, что по умолчанию запускается веб-сервер
CMD ["gunicorn", "evetradeanalyzer.wsgi:application", "--bind", "0.0.0.0:8000"]
