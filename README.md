# 🤖 DLBot — Professional Telegram Downloader Bot

A scalable, modular Telegram bot for downloading media from YouTube, Instagram, TikTok, Twitter/X and more.

## 🚀 Features & Project Status

**⚠️ IMPORTANT**: This project is **under active development**. See [ROADMAP.md](ROADMAP.md) for detailed progress tracking and [PROJECT_AUDIT_ANALYSIS.md](PROJECT_AUDIT_ANALYSIS.md) for known issues.

### Phase 1: MVP 🔄 ~40% IN PROGRESS

**Foundation & Architecture** ✅ COMPLETE:
- ✅ **Project structure** (bot/, modules/, services/, database/, web/, utils/)
- ✅ **Database models** (PostgreSQL + SQLAlchemy ORM with 9 models)
- ✅ **Module system** (pluggable architecture with auto-discovery)
- ✅ **Bot infrastructure** (aiogram 3.4.1 with middlewares)
- ✅ **Redis caching engine** (with TTL strategies)
- ✅ **Configuration management** (Pydantic v2 with environment support)

**Core Features** ⚠️ PARTIAL:
- 🔄 **YouTube downloader** (structure ready, yt-dlp integration needed)
- ⚠️ **Multi-language support** (middleware done, translation files empty)
- ⚠️ **User registration** (auth middleware done, full flow needs testing)
- ⚠️ **FSM download flow** (states defined, integration needs verification)
- ⚠️ **Subscription plans** (models created, enforcement middleware skeleton)
- ⚠️ **Admin commands** (partial implementation, needs testing)
- ❌ **Large file uploads** (Pyrogram setup done, logic not implemented)
- ❌ **Progress tracking** (utils stub exists, needs implementation)
- ❌ **Alembic migrations** (models exist, migration files empty)

**Testing Status**:
- ⚠️ Basic unit tests exist but coverage incomplete
- ❌ Full integration testing not yet performed
- ❌ FSM flow validation needed

### Phase 2: Monetization 🔄 ~40% IN PROGRESS

**Complete & Tested** ✅:
- ✅ **Beautiful Progress Bar** (Fully implemented: dynamic icons, 3s throttling, tested)
- ✅ **Referral & Coin System** (Complete: all integrations, models, handlers, tests)
- ✅ **Force-join channel middleware** (Complete)
- ✅ **Enhanced broadcast system** (Complete framework)

**Framework Ready** ✅ (HTML/API created, backend integration TBD):
- ✅ **Web Admin Panel** (FastAPI backend with 20+ endpoints)
   - ✅ JWT authentication system
   - ✅ Dashboard API (`/api/dashboard`)
   - ✅ Coin management API (`/api/coins/*`)
   - ✅ User management API (`/api/users/*`)
   - ✅ Broadcasting API (`/api/broadcasts`)
   - ✅ HTML templates with Chart.js (dashboard, users, coins, broadcasts)
   - ❌ Backend-template integration needs verification

**Blocked** 🔴 (Awaiting live credentials):
- ⏳ **CryptoBot payment integration** (0% - needs live API credentials)
- ⏳ **ZarinPal (Iranian Rial) gateway** (0% - needs live API credentials)

### Phase 3: Multi-Platform 🔄 ~5% IN PROGRESS

**Modules & Frameworks** ✅ (Code created, live testing TBD):
- ✅ **Instagram module** (instagrapi integration framework)
- ✅ **TikTok module** (yt-dlp integration framework)
- ✅ **Twitter/X module** (Tweepy integration framework)
- ✅ **Direct Link Downloader** (Generic HTTP/HTTPS framework)
- ✅ **Module auto-discovery system** (Priority-based with fallback)
- ✅ **Test suite** (37+ test cases for frameworks)
- ✅ **Documentation** (Implementation guides included)

**Real-World Testing** ❌ (Needs live platform access):
- ❌ Instagram download testing (requires valid credentials)
- ❌ TikTok download testing (requires rate limit verification)
- ❌ Twitter API testing (requires API keys)
- ❌ Direct download testing (needs sample URLs)

## 📋 Tech Stack

- **Bot Framework**: aiogram 3.4.1
- **Large File Uploads**: Pyrogram 2.0.106
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0
- **Cache**: Redis 7
- **Task Queue**: Celery 5.x
- **Web Panel**: FastAPI 0.110+
- **Config**: Pydantic v2
- **Logging**: loguru

## 📁 Project Structure

```
dlbot/
├── bot/                    # Bot logic (handlers, middlewares, states, keyboards)
├── modules/                # Pluggable downloader modules
├── services/               # Business logic (download, cache, user management)
├── database/               # Models, migrations, repositories
├── web/                    # FastAPI admin panel
├── utils/                  # Formatters, validators, helpers
├── locales/                # i18n translations
├── tasks/                  # Celery async tasks
├── config.py               # Settings management
└── main.py                 # Entry point
```

## 🛠️ Setup

### Prerequisites
- Python 3.11+ (tested with 3.12)
- PostgreSQL 15
- Redis 7
- Docker & Docker Compose (optional)

### Quick Installation

1. **Clone the repository:**
```bash
git clone <repo_url>
cd dlbot
```

2. **Create virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings:
# - BOT_TOKEN: Your Telegram bot token
# - DB_HOST, DB_USER, DB_PASSWORD: PostgreSQL credentials
# - REDIS_HOST: Redis connection
# - ADMIN_IDS: Comma-separated admin user IDs
# - PYROGRAM_APP_ID, PYROGRAM_APP_HASH: Telegram API credentials
```

5. **Initialize database:**
```bash
python init_project.py
alembic upgrade head
```

6. **Start the bot:**
```bash
python main.py
```

7. **Start web admin panel** (in another terminal):
```bash
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```

### Docker Setup

```bash
docker-compose up -d
```

This will start:
- Telegram Bot (aiogram)
- Web Admin Panel (FastAPI)
- PostgreSQL Database
- Redis Cache
- Celery Worker (optional)

## 📖 Module Development

### Creating a New Downloader

1. Create a new module in `modules/your_module/`:

```python
from modules.base import BaseDownloader, MediaInfo

class YourDownloader(BaseDownloader):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if URL matches this platform"""
        return "your-domain.com" in url
    
    async def fetch_info(self, url: str) -> MediaInfo:
        """Get video metadata"""
        # Implementation here
        return MediaInfo(
            url=url,
            title="Video Title",
            duration=120,
            formats=[...]
        )
    
    async def download(self, media_info: MediaInfo, output_path: str) -> str:
        """Download the media"""
        # Implementation here
        return "/path/to/downloaded/file"
```

2. The module auto-registers via `from modules import register_module`

3. The registry automatically calls `can_handle()` to route URLs to the correct downloader

### Example: YouTube Module
- URL Detection: `youtube.com`, `youtu.be`, `youtube-nocookie.com`
- Format Parser: Groups video/audio/combined formats by quality
- Download: Async yt-dlp with progress callbacks
- Quality Presets: best, good, medium, low, audio-only

## 🔌 API Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `BOT_TOKEN`: Telegram bot token
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `REDIS_HOST`: Redis connection
- `PYROGRAM_APP_ID`, `PYROGRAM_APP_HASH`: Telegram API credentials
- `ADMIN_IDS`: Comma-separated admin user IDs

## 📊 Database Models

- **User**: User accounts, preferences, statistics
- **Download**: Download history and metadata
- **CachedFile**: Telegram file_id caching
- **Plan**: Subscription tier definitions
- **Subscription**: User subscription status
- **Referral**: Referral tracking and referrer relationships
- **CoinTransaction**: Coin ledger for earnings
- **Payment**: Payment transaction history
- **Channel**: Force-join channel configuration

## 🚦 Key Commands

### User Commands
- `/start` - Initialize bot + language selection
- `/help` - Help information
- `/profile` - View user profile & stats
- `/history` - Download history
- `/plans` - View subscription plans
- `/referral` - Referral information
- (Send URL) - Download media

### Admin Commands
- `/admin` - Admin dashboard menu
- `/stats` - Bot statistics (users, downloads, revenue)
- `/broadcast` - Send message to all users
- `/users` - User management
- `/channels` - Manage force-join channels

## 🌐 Web Admin Panel

Access at `http://localhost:8000`

### API Endpoints

**Dashboard:**
- `GET /api/dashboard/overview` - Overview metrics
- `GET /api/dashboard/stats` - Detailed statistics
- `GET /api/dashboard/charts/*` - Chart data

**Users:**
- `GET /api/users/` - List users
- `GET /api/users/{user_id}` - User details
- `POST /api/users/{user_id}/ban` - Ban user
- `POST /api/users/{user_id}/plan` - Change plan

**Broadcasts:**
- `GET /api/broadcast/` - Broadcast history
- `POST /api/broadcast/send` - Send broadcast
- `GET /api/broadcast/{id}` - Broadcast details

**Plans:**
- `GET /api/plans/` - List plans
- `POST /api/plans/` - Create plan
- `PUT /api/plans/{id}` - Update plan

**Payments:**
- `GET /api/payments/` - Payment history
- `POST /api/payments/{id}/refund` - Process refund

**Settings:**
- `GET /api/settings/` - Current settings
- `PUT /api/settings/` - Update settings
- `POST /api/settings/cache/clear` - Clear Redis cache

## 🔐 Security

- Admin commands require verified admin ID
- User authentication via Telegram ID
- Password hashing with bcrypt (for web panel)
- JWT tokens for API authentication
- Rate limiting on downloads

## 📝 License

See LICENSE file for details.

## 👥 Contributing

Contributions welcome! Please create a pull request.

## 📧 Support

For issues and questions, please create a GitHub issue.

## 📚 Documentation & Progress Tracking

For detailed information about project status and development roadmap, please refer to:

- **[ROADMAP.md](ROADMAP.md)** - Detailed task breakdown by phase with accurate completion percentages
- **[PROJECT_AUDIT_ANALYSIS.md](PROJECT_AUDIT_ANALYSIS.md)** - 12 identified issues with analysis and solutions
- **[PHASED_IMPLEMENTATION_ROADMAP.md](PHASED_IMPLEMENTATION_ROADMAP.md)** - Master implementation plan with file inventory
- **[IMPLEMENTATION_DETAILS_GUIDE.md](IMPLEMENTATION_DETAILS_GUIDE.md)** - Step-by-step instructions for each task
- **[AI_AGENT_PROMPT.md](AI_AGENT_PROMPT.md)** - AI workflow for automated task execution
- **[QUICK_AUDIT_CHECKLIST.md](QUICK_AUDIT_CHECKLIST.md)** - Executive summary for quick overview
- **[HOW_TO_USE_AUDIT_REPORTS.md](HOW_TO_USE_AUDIT_REPORTS.md)** - Guide for different team roles

### Quick Status Overview

- **Phase 1**: 🔄 ~40% Complete (Foundation ready, core features in progress)
- **Phase 2**: 🔄 ~40% Complete (Progress bar ✅, Coin system ✅, Web panel framework ready)
- **Phase 3**: 🔄 ~5% Complete (Module frameworks ready, live testing TBD)

For the most up-to-date accurate status, see [ROADMAP.md](ROADMAP.md).

---

**Status**: 🔄 Active Development (Phase 1 MVP - ~40% Complete)
