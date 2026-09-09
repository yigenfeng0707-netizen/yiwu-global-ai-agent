FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# P3-2 持久化策略：
#   - 本地 / docker-compose：声明 VOLUME /app/data，建议挂 named volume 保留
#     SQLite (app.db + WAL) 与 LLM 日计数（已迁 SQLite llm_daily_count 表）。
#   - 魔搭创空间：平台提供 /mnt/workspace 持久卷，deploy-modelscope.yml 通过
#     `upsert variables DATABASE_PATH "/mnt/workspace/data/app.db"` 注入，容器
#     重启数据不丢。线上 Dockerfile 在 deploy/modelscope/（无 HEALTHCHECK / VOLUME，
#     避免干扰平台就绪判定）。
VOLUME /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=5).status==200 else 1)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
