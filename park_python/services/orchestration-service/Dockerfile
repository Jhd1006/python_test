# 1단계: 빌드 스테이지
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------

# 2단계: 실행 스테이지
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    tzdata \ 
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

# [수정포인트 1] settings_orchestration.py가 위치한 park_py 폴더도 필요합니다.
COPY manage.py .
COPY park_py/ ./park_py/ 
COPY shared/ ./shared/
COPY contracts/ ./contracts/
COPY services/ ./services/
COPY scripts/ ./scripts/

# [수정포인트 2] PYTHONPATH에 src 디렉토리를 더 정확히 매핑합니다.
# settings.py가 sys.path.insert를 하지만, 환경변수로 잡아주는 것이 gunicorn 실행 시 에러를 방지합니다.
ENV PYTHONPATH="/app:/app/services/orchestration-service/src:/app/contracts/gen/python"
# 실행할 설정 파일 지정
ENV DJANGO_SETTINGS_MODULE=orchestration_service.settings

RUN chmod +x scripts/services/orchestration/*.sh && \
    chmod +x scripts/services/_common.sh

EXPOSE 8000

# run_http.sh 내부에서 gunicorn을 실행할 때 환경변수들이 잘 전달됩니다.
CMD ["./scripts/services/orchestration/run_http.sh"]
