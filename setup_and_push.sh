#!/usr/bin/env bash
set -euo pipefail

# setup_and_push.sh
# Usage:
#   chmod +x setup_and_push.sh
#   ./setup_and_push.sh
#
# This script does the following steps:
#   1. Verify git repository exists
#   2. Create safe example config files (.env.example, config.example.py, etc.)
#   3. Update .gitignore to ignore local secret files
#   4. Remove sensitive files from git tracking if already added
#   5. Stage example files and .gitignore changes
#   6. Commit the changes
#   7. Push to GitHub origin/main branch
#
# Important:
#   - Do NOT commit real secrets or tokens
#   - GitHub may ask for username/password or personal access token
#   - This script only commits example/template files, not real secrets

REPO_ROOT="$(pwd)"

function info() {
  echo -e "\033[1;34m[INFO]\033[0m $*"
}

function warn() {
  echo -e "\033[1;33m[WARN]\033[0m $*"
}

function error() {
  echo -e "\033[1;31m[ERROR]\033[0m $*"
  exit 1
}

function ensure_git_repo() {
  if [ ! -d ".git" ]; then
    error "Not a git repository. Please run this script from your project root directory."
  fi
}

function ensure_git_installed() {
  if ! command -v git >/dev/null 2>&1; then
    error "Git is not installed. Please install Git first."
  fi
}

function create_env_example() {
  if [ ! -f ".env" ]; then
    warn ".env file not found. Please create your .env file first, then run this script again."
    return
  fi

  info "Creating/updating .env.example from .env"
  cp .env .env.example.tmp

  sed -i -E \
    -e 's~^(BOT_TOKEN)=.*$~\1=YOUR_TELEGRAM_BOT_TOKEN~' \
    -e 's~^(ADMIN_IDS)=.*$~\1=YOUR_ADMIN_USER_IDS_COMMA_SEPARATED~' \
    -e 's~^(DB_PASSWORD)=.*$~\1=YOUR_DB_PASSWORD~' \
    -e 's~^(ADMIN_WEB_PASSWORD)=.*$~\1=YOUR_WEB_ADMIN_PASSWORD~' \
    -e 's~^(PYROGRAM_APP_ID)=.*$~\1=YOUR_PYROGRAM_APP_ID~' \
    -e 's~^(PYROGRAM_APP_HASH)=.*$~\1=YOUR_PYROGRAM_APP_HASH~' \
    -e 's~^(CRYPTOBOT_API_TOKEN)=.*$~\1=YOUR_CRYPTOBOT_API_TOKEN~' \
    -e 's~^(NOWPAYMENTS_API_KEY)=.*$~\1=YOUR_NOWPAYMENTS_API_KEY~' \
    -e 's~^(ZARINPAL_MERCHANT_ID)=.*$~\1=YOUR_ZARINPAL_MERCHANT_ID~' \
    -e 's~^(JWT_SECRET_KEY)=.*$~\1=YOUR_JWT_SECRET_KEY~' \
    -e 's~^(.+_PASSWORD)=.*$~\1=YOUR_PASSWORD_VALUE~' \
    .env.example.tmp || true

  mv .env.example.tmp .env.example
}

function create_docker_compose_example() {
  if [ -f "docker-compose.example.yml" ]; then
    info "docker-compose.example.yml already exists."
    return
  fi

  info "Creating docker-compose.example.yml"
  cat > docker-compose.example.yml <<'EOF'
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    container_name: dlbot_postgres
    environment:
      POSTGRES_DB: dlbot_db
      POSTGRES_USER: dlbot_user
      POSTGRES_PASSWORD: YOUR_POSTGRES_PASSWORD
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: dlbot_redis
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  dlbot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dlbot_bot
    command: python main.py
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      DB_HOST: postgres
      DB_USER: dlbot_user
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: dlbot_db
      REDIS_HOST: redis
      REDIS_PORT: 6379
      PYROGRAM_APP_ID: ${PYROGRAM_APP_ID}
      PYROGRAM_APP_HASH: ${PYROGRAM_APP_HASH}
    volumes:
      - .:/app
      - temp_downloads:/app/temp_downloads
      - cached_files:/app/cached_files
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  web_panel:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dlbot_web_panel
    command: uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
    environment:
      DB_HOST: postgres
      REDIS_HOST: redis
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  temp_downloads:
  cached_files:
EOF
}

function create_alembic_example() {
  if [ -f "alembic.example.ini" ]; then
    info "alembic.example.ini already exists."
    return
  fi

  info "Creating alembic.example.ini"
  cat > alembic.example.ini <<'EOF'
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = postgresql+asyncpg://dlbot_user:YOUR_DB_PASSWORD@localhost:5432/dlbot_db
sqlalchemy.echo = false
sqlalchemy.pool_pre_ping = true
sqlalchemy.poolclass = sqlalchemy.pool.NullPool

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF
}

function create_config_example() {
  if [ -f "config.example.py" ]; then
    info "config.example.py already exists."
    return
  fi

  info "Creating config.example.py"
  cat > config.example.py <<'EOF'
"""
Example configuration file.
Copy this file to config.py and replace placeholder values with your own secrets.
Do NOT commit real secret values to GitHub.
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional

class DatabaseSettings(BaseSettings):
    db_type: str = Field("sqlite", description="Database type (sqlite or postgresql)")
    host: str = Field("localhost", description="PostgreSQL host")
    port: int = Field(5432, description="PostgreSQL port")
    user: str = Field("dlbot_user", description="Database user")
    password: str = Field("YOUR_DB_PASSWORD", description="Database password")
    name: str = Field("dlbot_db", description="Database name")
    path: str = Field("./dlbot.db", description="SQLite database path")

    class Config:
        env_prefix = "DB_"
        case_sensitive = False

class RedisSettings(BaseSettings):
    host: str = Field("localhost", description="Redis host")
    port: int = Field(6379, description="Redis port")
    db: int = Field(0, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")

    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False

class TelegramBotSettings(BaseSettings):
    token: str = Field("", description="Telegram Bot API token")
    admin_ids: List[int] = Field(default_factory=list, description="Admin user IDs")

    class Config:
        env_prefix = "BOT_"
        case_sensitive = False

class PyrogramSettings(BaseSettings):
    app_id: int = Field(0, description="Telegram App ID")
    app_hash: str = Field("YOUR_PYROGRAM_APP_HASH", description="Telegram App Hash")

    class Config:
        env_prefix = "PYROGRAM_"
        case_sensitive = False

class WebPanelSettings(BaseSettings):
    jwt_secret_key: str = Field("YOUR_JWT_SECRET_KEY", description="JWT secret key")

    class Config:
        env_prefix = "WEB_"
        case_sensitive = False

class AppSettings(BaseSettings):
    env: str = Field("development", description="Environment")
    debug: bool = Field(True, description="Debug mode")

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    telegram: TelegramBotSettings = Field(default_factory=TelegramBotSettings)
    pyrogram: Optional[PyrogramSettings] = Field(default_factory=PyrogramSettings)
    web_panel: WebPanelSettings = Field(default_factory=WebPanelSettings)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
EOF
}

function update_gitignore() {
  info "Ensuring .gitignore contains sensitive file patterns"
  local entries=(
    ".env"
    "config.py"
    "alembic.ini"
    "docker-compose.override.yml"
  )

  for entry in "${entries[@]}"; do
    if ! grep -qFx "$entry" .gitignore 2>/dev/null; then
      echo "$entry" >> .gitignore
      info "Added $entry to .gitignore"
    fi
  done
}

function untrack_sensitive_files() {
  if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    warn ".env was tracked in git. Removing from tracking..."
    git rm --cached .env || true
  fi

  if git ls-files --error-unmatch config.py >/dev/null 2>&1; then
    warn "config.py was tracked in git. Removing from tracking..."
    git rm --cached config.py || true
  fi

  if git ls-files --error-unmatch alembic.ini >/dev/null 2>&1; then
    warn "alembic.ini was tracked in git. Removing from tracking..."
    git rm --cached alembic.ini || true
  fi
}

function git_add_commit_push() {
  local branch
  branch=$(git branch --show-current)
  if [ "$branch" != "main" ]; then
    info "Current branch is $branch. Switching to main..."
    git branch -M main
  fi

  info "Staging files for commit"
  git add .gitignore .env.example docker-compose.example.yml alembic.example.ini config.example.py

  if git diff --cached --quiet; then
    info "No new changes to commit."
  else
    git commit -m "Add secure example config files and ignore local secrets"
    info "Commit completed."
  fi

  if git remote get-url origin >/dev/null 2>&1; then
    info "Remote origin already configured."
  else
    read -r -p "Enter your GitHub repository URL (e.g. https://github.com/yekaweb/Max-Downloader.git): " remote_url
    git remote add origin "$remote_url"
  fi

  info "Pushing to origin main..."
  git push -u origin main
}

function show_before_start() {
  echo "========================================"
  echo "This script will:"
  echo "  1. Create example config files"
  echo "  2. Update .gitignore for sensitive files"
  echo "  3. Remove sensitive files from git tracking"
  echo "  4. Commit changes"
  echo "  5. Push to GitHub"
  echo ""
  echo "GitHub may ask for username and password/token."
  echo "Press Enter to continue..."
  echo "========================================"
  read -r
}

ensure_git_installed
ensure_git_repo
show_before_start
create_env_example
create_docker_compose_example
create_alembic_example
create_config_example
update_gitignore
untrack_sensitive_files
git_add_commit_push

info "Done! Your repository has been pushed to GitHub with example config files."