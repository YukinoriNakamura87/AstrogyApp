FROM python:3.11-slim

WORKDIR /app

# kerykeion の依存 pyswisseph（C/C++拡張）のビルドに必要
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --reload でホットリロード有効（開発環境用）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
