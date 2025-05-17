<p align="center">
    <img src="./docs/logo.png" alt="XBuddy Logo" />
</p>

---

# Xbuddy Backend API (v2.0)

[![Official Website](https://img.shields.io/badge/Website-xbuddy.me-blue)](https://xbuddy.me/)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Stable-green)
[![Legacy Version](https://img.shields.io/badge/Legacy_v1.0-Archived-lightgrey)](https://github.com/xbuddy/legacy-api)

XBuddy is a desktop pet application, and this repository contains its **backend service (FastAPI)**. The backend provides APIs for news feeds, phishing link detection, Twitter/token analysis, AI chat, chat content recognition, and emotion reminders.

> **Note:** This is the current stable version (v2.0) of the XBuddy API. The legacy version (v1.0) has been archived and is no longer maintained. If you're migrating from v1.0, please see the [Migration Guide](#-migration-from-v10) below.

## 🚀 Features

- 📰 **News Feed** - Automatically fetches the latest information
- 🎣 **Phishing Link Detection** - Protects users' online security
- 🤖 **AI Chat** - Intelligent conversation and sentiment analysis
- 📊 **Data Analysis** - Twitter/token trend tracking

## 📁 Directory Structure

```
xbuddy_backend/
├── app/                # Application code
│   ├── api/            # Routes layer
│   │   └── stream/     # Streaming API endpoints
│   ├── schemas/        # Request/Response Pydantic Schema
│   ├── services/       # Business logic
│   │   ├── agent/      # AI agent services
│   │   └── external/   # External API integrations
│   ├── utils/          # Utility functions
│   ├── config.py       # YAML configuration loader
│   ├── dependencies.py # Common dependencies
│   ├── main.py         # FastAPI entry point
│   └── run.py          # Production entry point
├── static/             # Static files
├── config.yaml.example # YAML configuration example, loaded via `CONFIG_FILE` env var
├── config.yaml         # Configuration file (create from example)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Backend image
├── docker-compose.yaml # One-click startup (PostgreSQL + Redis + Service)
├── run_dev.bat         # Windows development script
├── run_dev.sh          # Linux/macOS development script
├── run_server.bat      # Windows production server script
├── .gitignore          # Git ignore file
└── README.md           # Documentation
```

## 📜 Command Scripts

### Development Scripts

#### `run_dev.bat` (Windows) / `run_dev.sh` (Linux/macOS)
These scripts have two modes:
1. **Build Mode**: `run_dev.bat build` or `run_dev.sh build`
   - Builds the Docker image for the XBuddy API
   - Creates a Docker image tagged as `xbuddy-api:latest`

2. **Development Mode**: `run_dev.bat` or `run_dev.sh`
   - Starts the application in development mode with auto-reload
   - Runs the FastAPI application using Uvicorn
   - Serves on `0.0.0.0:8080` (accessible from any network interface)
   - Enables hot reload for code changes

### Production Script

#### `run_server.bat` (Windows)
- Starts the XBuddy API service in production mode
- Runs the application using the entry point module `app.run`
- No auto-reload (for stable production environment)

## 🚀 Quick Start

### 1. Clone the project and enter the directory
```bash
git clone <repo-url> && cd xbuddy_backend
```

### 2. Create and modify configuration
```bash
cp config.yaml.example config.yaml
# Modify API Keys, database connection parameters, etc.
```

### 3. Local Development (requires PostgreSQL / Redis)

Install dependencies:

```bash
conda create -n xbuddy-api python=3.12
pip install -r ./requirements.txt
```

Start (Linux/macOS):
```bash
export CONFIG_FILE=$(pwd)/config.yaml
./run_dev.sh
```

Start (Windows):
```bat
set CONFIG_FILE=%cd%\config.yaml
run_dev.bat
```

### 4. Docker Quick Start
```bash
docker-compose up -d --build
```

### 5. Access Documentation

Once the service is running, visit: <http://localhost:8080/> to view the Swagger documentation.

## ⚙️ Important Environment Variables
| Variable Name | Description | Default |
|---------------|-------------|----------|
| `CONFIG_FILE` | YAML configuration file path | `./config.yaml` |

## 💡 Design Highlights
- **FastAPI** + **Uvicorn**: Asynchronous high performance.
- **SQLAlchemy**: Asynchronous ORM for PostgreSQL operations.
- **redis.asyncio**: Caching active chat contexts.
- **YAML Single File Configuration**: Easy to maintain, supports multi-environment via Docker environment variables override.
- **Modular**: API/Service/Model separated by layers, code is easily extensible.

## 📋 Technology Stack
- ![FastAPI](https://img.shields.io/badge/FastAPI-Web_Framework-009688?style=flat-square&logo=fastapi)
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat-square&logo=postgresql)
- ![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=flat-square&logo=redis)
- ![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=flat-square&logo=docker)
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-3776AB?style=flat-square)

## 🔄 Migration from v1.0
> **⚠️ Important Notice:** The legacy v1.0 API was officially deprecated and archived on **2025-04-24**. All services using the old endpoints should migrate to this version as soon as possible.

**Key differences from the old API:**

- Completely rewritten using the modern FastAPI framework (v1.0 was Flask)
- Asynchronous database operations for much higher performance
- AI chat streaming responses for enhanced intelligence
- Most API endpoints and response formats have significantly changed

**Migration steps:**

1. Update your client to use the new authentication endpoints
2. Refactor API calls according to the new documentation
3. Thoroughly test before going live

> The legacy API documentation is available for reference in the [archived repository](https://github.com/xbuddy-ai/xbuddy-api).

## 📋 Version History

| Version | Release Date | Status       | Notes |
|---------|-------------|--------------|-------|
| v2.0.0  | 2025-05-10  | Current      | v2 officially released |
| v1.0.0  | 2025-04-24  | Deprecated   | [Archived Repository](https://github.com/xbuddy-ai/xbuddy-api) |

## 📄 License <a name="license"></a>

This project is licensed under the [CC BY-NC](./LICENSE) License (Creative Commons Attribution-NonCommercial).