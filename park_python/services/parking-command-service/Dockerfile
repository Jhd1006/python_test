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

# 트리 구조에 맞춘 소스 복사
COPY manage.py .
COPY park_py/ ./park_py/
COPY shared/ ./shared/
COPY contracts/ ./contracts/
COPY services/ ./services/
COPY scripts/ ./scripts/

# [수정포인트] Command 서비스 전용 환경 설정
ENV PYTHONPATH="/app:/app/services/parking-command-service/src:/app/contracts/gen/python"
# settings 경로는 실제 프로젝트 구조(parking_command_service/settings.py)에 맞춤
ENV DJANGO_SETTINGS_MODULE=parking_command_service.settings

RUN chmod +x scripts/services/parking-command/*.sh && \
    chmod +x scripts/services/_common.sh

# gRPC 기본 포트 (필요 시 수정)
EXPOSE 50051

# 오케스트레이션의 명령을 받기 위해 gRPC 런타임 실행
CMD ["./scripts/services/parking-command/run_grpc.sh"]
