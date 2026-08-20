# 魔搭创空间专用 Dockerfile（服务必须监听 0.0.0.0:7860）
# 前端产物由 GitHub Actions 预构建为 web_dist/，此处只装 Python 依赖
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY web_dist ./web_dist

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
