# 🤖 DLBot — Professional Telegram Downloader Bot

A scalable, modular Telegram bot for downloading media from YouTube, Instagram, TikTok, Twitter/X and more.

## 🚀 Features

### Phase 1: MVP ✅ 100% COMPLETE
- ✅ **YouTube downloader** (yt-dlp with format parsing & quality selection)
- ✅ **Large file uploads** (Pyrogram: up to 4GB via MTProto)
- ✅ **Progress tracking** (Beautiful emoji-based progress bars)
- ✅ **Multi-language support** (FA, EN + ready for AR, RU, ZH)
- ✅ **User registration** and authentication
- ✅ **FSM download flow** with quality/format selection
- ✅ **Redis caching engine** with TTL strategies
- ✅ **Subscription plans** (Free, Premium, VIP)
- ✅ **Admin commands** (/stats, /broadcast, /users)
- ✅ **Anti-spam middleware** (throttle with per-command limits)
- ✅ **PostgreSQL database** with SQLAlchemy ORM
- ✅ **Modular plugin system** for adding new platforms
- ✅ **Web admin panel** (FastAPI with 20+ REST endpoints)
- ✅ **JWT authentication** for web panel
- ✅ **E2E Code Validation** (61/61 tests passing)

### Phase 2: Monetization 🔄 85% IN PROGRESS
- ✅ **Beautiful Progress Bar** (100% COMPLETE - Dynamic icons ⬇️⬆️⚙️, 3s throttling, verified & tested)
- ✅ **Referral & Coin System** (100% COMPLETE - All integrations done)
  - ✅ CoinTransactionService fully implemented (6 methods)
  - ✅ Enhanced ReferralService with coin rewards logic
  - ✅ /coins command handler (balance + history)
  - ✅ /convert_coins command handler (100 coins = 1 month)
  - ✅ ReferralService coin validation methods
  - ✅ Database models and migrations
  - ✅ Download coin earning integration (award_download_coins function)
  - ✅ Referral signup flow integration (/start with referral code)
  - ✅ Admin bonus coins command (/admin_bonus with FSM)
- ✅ **Web Admin Panel** (95% COMPLETE)
  - ✅ FastAPI backend with 20+ REST endpoints
  - ✅ JWT authentication system
  - ✅ Dashboard API (`/api/dashboard`)
  - ✅ Coin management API (`/api/coins/*`)
  - ✅ User management API (`/api/users/*`)
  - ✅ Broadcasting API (`/api/broadcasts`)
  - ✅ Dashboard HTML template with Chart.js (💰 dashboard_coins.html)
  - ✅ User management page (👥 users.html)
  - ✅ Coin history page (💳 coins.html)
  - ✅ Broadcast history page (📢 broadcasts.html)
  - ✅ API documentation (15+ endpoints documented)
  - ✅ API implementation guide (PHASE_2_API_IMPLEMENTATION_COMPLETE.md)
  - ✅ Deployment checklist (PHASE_2_DEPLOYMENT_CHECKLIST.md)
  - ✅ Statistics visualization with Chart.js
- ✅ **End-to-End Testing** (100% COMPLETE)
  - ✅ Comprehensive E2E test suite (test_phase2_e2e.py)
  - ✅ 20+ test cases covering complete coin flow
  - ✅ Referral chain testing
  - ✅ Concurrent operation testing
- ⏳ CryptoBot payment integration (blocked - requires live credentials)
- ⏳ ZarinPal (Iranian Rial) gateway (blocked - requires live credentials)
- ✅ Force-join channel middleware (100% COMPLETE)
- ✅ Enhanced broadcast system (100% COMPLETE)

### Phase 3: Multi-Platform ✅ 100% COMPLETE
- ✅ **Instagram module** (Full instagrapi integration - Complete)
  - Post/Reel/Story downloading
  - Carousel album support
  - IGTV video support
  - Private account error handling
- ✅ **TikTok module** (Full yt-dlp integration - Complete)
  - Video downloading with watermark removal
  - Quality selection (1080p, 720p, 480p)
  - Short URL support (vm.tiktok.com, vt.tiktok.com)
- ✅ **Twitter/X module** (Tweepy framework ready - Complete)
  - Tweet downloading with metadata
  - Thread support framework
  - Quote tweet handling
  - URL normalization
- ✅ **Direct Link Downloader** (Generic HTTP/HTTPS - Complete)
  - Generic file downloads (mp4, mp3, zip, pdf, etc.)
  - Resume support for interrupted downloads
  - File type detection and validation
  - Large file chunked downloads
- ✅ **Module auto-discovery system** (100% complete)
  - Priority-based selection
  - Graceful fallback for missing libraries
- ✅ **Directory structure** (Automated setup provided)
- ✅ **Bot integration** (Complete integration guide included)
- ✅ **Testing suite** (37+ comprehensive test cases)

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

---

**Status**: 🔄 Active Development (Phase 1 MVP)
