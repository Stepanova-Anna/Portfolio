FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование protobuf файла
COPY protobufs/glossary.proto ./protobufs/

# Генерация Python кода из .proto файла
RUN python -m grpc_tools.protoc \
    -I./protobufs \
    --python_out=. \
    --pyi_out=. \
    --grpc_python_out=. \
    ./protobufs/glossary.proto

# Копирование исходного кода
COPY . .

EXPOSE 50051

# Запуск сервиса
CMD ["python", "server.py"]