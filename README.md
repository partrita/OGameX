<div align="center">

# 🌌 OGameX (Python FastAPI & uv Edition)

**Next-Gen Open-Source OGame Redesign Clone with High-Performance Python Core**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/Package%20Manager-uv-DE5FE9?logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 소개 (Introduction)

**OGameX**는 초고속 Rust 기반 Python 패키지 매니저인 **`uv`**로 의존성을 관리하며, **FastAPI**, **실시간 WebSocket**, **Noto Sans CJK 다국어 Glassmorphism SPA** 및 **Docker Compose**로 구동되는 현대적인 우주 전략 시뮬레이션 게임 엔진입니다.

---

## ⚡ 주요 특징 (Key Features)

- **Next-Gen Dependency Management with `uv`**: `pip`/수동 `venv` 관리의 번거로움 없이 `uv sync`, `uv run`으로 10~100배 빠른 패키지 해결 및 자동 실행
- **High-Performance Async Backend**: `FastAPI` + `Pydantic V2` + `SQLAlchemy 2.0 (asyncio)`
- **Real-Time WebSockets**: 행성 자원 틱 및 함대 비행 알림 실시간 동기화
- **Multi-Language (KO / EN)**: Noto Sans CJK 기반 한글/영문 실시간 언어 전환 지원
- **Ultra-Fast Rust Battle Engine**: 대규모 함대 전투 시뮬레이션 고성능 FFI 연동
- **Dockerized One-Click Deploy**: `docker-compose` 단일 명령어로 Backend, Frontend, MySQL, Redis 완벽 오케스트레이션

---

## 🚀 빠른 시작 (Quick Start with Docker Compose)

```bash
# 1. 저장소 클론 및 이동
git clone https://github.com/lanedirt/OGameX.git
cd OGameX

# 2. Docker Compose 빌드 및 실행
docker-compose up -d --build
```

### 🌐 서비스 접속 안내
- **메인 게임 웹 인터페이스**: [http://localhost](http://localhost) (포트 80)
- **FastAPI 대화형 API 문서 (Swagger UI)**: [http://localhost/docs](http://localhost/docs)

---

## 🛠️ 로컬 개발 환경 (Local Development with uv)

수동으로 `venv`를 만들고 활성화할 필요가 없습니다. `uv`가 프로젝트 루트의 `pyproject.toml`과 `uv.lock`을 기반으로 모든 환경을 자동으로 격리 관리합니다.

### 1. 의존성 동기화 (최초 1회)
```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 자동 동기화
uv sync
```

### 2. 백엔드 개발 서버 실행
```bash
# uv run으로 가상환경 진입 없이 바로 실행
uv run uvicorn python.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 테스트 실행 (Pytest)
```bash
uv run pytest python/tests/
```

---

## 📂 프로젝트 구조 (Project Structure)

```text
.
├── pyproject.toml             # uv 표준 프로젝트 및 의존성 정의
├── uv.lock                    # 초고속/재현 가능한 의존성 잠금 파일
├── docker-compose.yml         # 전체 컨테이너 오케스트레이션
├── Dockerfile                 # uv 기반 초경량/초고속 FastAPI 백엔드 이미지
├── nginx.conf                 # Nginx 리버스 프록시 및 정적 자산 라우팅
├── frontend/                  # Glassmorphism SPA 프론트엔드 (다국어 지원)
│   ├── index.html
│   └── src/ (main.js, style.css, i18n.js)
├── python/                    # FastAPI 비동기 백엔드
│   ├── app/ (core, game_objects, models, routers, schemas, services)
│   └── tests/ (pytest 테스트 스위트)
└── rust/                      # 고성능 FFI 전투 시뮬레이션 라이브러리
```

---

## 📜 라이선스 (License)

본 프로젝트는 [MIT License](LICENSE)를 따릅니다.
