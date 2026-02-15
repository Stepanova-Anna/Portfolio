FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование protobuf файлов и генерация кода
COPY ../protobufs/glossary.proto ./protobufs/
RUN python -m grpc_tools.protoc \
    -I./protobufs \
    --python_out=. \
    --pyi_out=. \
    --grpc_python_out=. \
    ./protobufs/glossary.proto

# Копирование исходного кода
COPY gateway.py .

EXPOSE 5000

CMD ["python", "gateway.py"]