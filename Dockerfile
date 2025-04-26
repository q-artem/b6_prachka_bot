# Используем Python 3.11 на базе Alpine
FROM python:3.12
# Устанавливаем рабочую директорию
WORKDIR /usr/src/app/
# Копируем файлы приложения в контейнер
COPY . /usr/src/app/
# Устанавливаем зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска Flask-приложения
CMD ["python", "main.py"]