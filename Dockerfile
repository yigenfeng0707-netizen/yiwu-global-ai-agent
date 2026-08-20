FROM python:3.12-slim

WORKDIR /app

# install dependencies first (better layer caching)
COPY demo/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy backend source
COPY demo /app

ENV PYTHONUNICODE=utf-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV COMPETITOR_RESEARCH_ENABLED=true
ENV ENABLE_LIVE_COMPETITOR=0
ENV REMIO_LIVE_CLI=auto

EXPOSE 8000

CMD ["python", "-m", "app.main"]
