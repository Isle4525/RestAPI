# Используем легкий образ Python
FROM python:3.10-slim

# Устанавливаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код (кроме того, что в .gitignore)
COPY . .

# Команда для запуска (укажи свой главный файл, если он не app.py)
CMD ["python", "main.py"]
