FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をインストール
COPY streamlit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
# 親ディレクトリのdb/とconstants/もコピー（既存のコードを再利用するため）
COPY db/ ../db/
COPY constants/ ../constants/
COPY common/ ../common/
COPY streamlit/ ./streamlit/

# ポートを公開
EXPOSE 8501

# Streamlitを起動
CMD ["streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

