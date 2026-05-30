# 🧪 DLBot Integration Testing Guide
**Status**: Ready for Full Integration Testing  
**Date**: 2026-05-23

---

## 📋 Integration Test Scenarios

This guide covers how to test the complete end-to-end bot workflow.

---

## 🔧 TEST ENVIRONMENT SETUP

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Redis 7
- Telegram Bot Account (get from @BotFather)
- Pyrogram Credentials (get from my.telegram.org)

### Quick Docker Setup
```bash
# Terminal 1: PostgreSQL
docker run --name dlbot-postgres \
  -e POSTGRES_USER=dlbot_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=dlbot_db \
  -p 5432:5432 \
  -d postgres:15

# Terminal 2: Redis
docker run --name dlbot-redis \
  -p 6379:6379 \
  -d redis:7

# Terminal 3: Project
cd /path/to/dlbot
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

---

## 🎯 TEST SCENARIO 1: Basic Bot Startup

### Setup
```bash
cp .env.example .env
# Edit .env with:
BOT_TOKEN=your_token_here
PYROGRAM_APP_ID=12345
PYROGRAM_APP_HASH=your_hash_here
DB_HOST=localhost
DB_USER=dlbot_user
DB_PASSWORD=secure_password
REDIS_HOST=localhost
ADMIN_IDS=123456789
```

### Test Steps
```bash
# 1. Initialize database
python init_project.py

# 2. Run migrations
alembic upgrade head

# 3. Start bot
python main.py
```

### Expected Results
```
✅ [INFO] 🤖 Starting DLBot v1.0.0
✅ [INFO] 📊 Environment: development
✅ [INFO] 🌐 Default Language: fa
✅ [INFO] ✅ Bot components loaded successfully
✅ [INFO] 🔌 Connecting to database...
✅ [INFO] ✅ Database connection established
```

### Verification
- Check logs for any errors
- Verify PostgreSQL tables created
- Confirm Redis connection working

---

## 🎯 TEST SCENARIO 2: User Registration Flow

### Test Steps
1. **Send `/start` command**
   ```
   User: /start
   Bot Response: Displays language selection keyboard
   ```

2. **Expected Bot Response**
   ```
   Message: "سلام! به DLBot خوش آمدید. (زبان: fa)"
   Keyboard: 🇮🇷 Persian | 🇬🇧 English | 🇸🇦 Arabic | 🇷🇺 Russian | 🇨🇳 Chinese
   ```

3. **Select Language**
   ```
   User: Clicks "🇬🇧 English"
   Bot Response: "Welcome to DLBot! Please select your language."
   ```

### Verification Points
- [x] User record created in database
- [x] Language preference stored
- [x] Middleware auth triggered
- [x] User appears in `/stats` command

---

## 🎯 TEST SCENARIO 3: Download Flow with YouTube

### Test Steps
1. **Send YouTube URL**
   ```
   User: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   Bot Response: "Fetching video information..."
   ```

2. **Expected Information Fetch**
   ```
   Video: "Rick Astley - Never Gonna Give You Up"
   Duration: 3:33
   Uploader: Rick Astley
   Views: 1.2B+
   
   [Quality Selection Keyboard]
   1080p | 720p | 480p | Audio Only
   ```

3. **Select Quality**
   ```
   User: Clicks "720p"
   Bot Response: "Starting download... (progress bar)"
   ```

4. **Monitor Progress**
   ```
   ▰▰▰▱▱▱▱▱▱▱ 30% | ⚡ 2.5MB/s | ⏱ 1m 23s remaining
   ▰▰▰▰▰▱▱▱▱▱ 50% | ⚡ 2.8MB/s | ⏱ 0m 50s remaining
   ▰▰▰▰▰▰▰▰▰▰ 100% | ⚡ 2.5MB/s | ✅ Complete!
   ```

5. **File Upload to Telegram**
   ```
   Bot Response: Uploads MP4 file via Pyrogram
   Caption: "Rick Astley - Never Gonna Give You Up (720p)"
   ```

### Verification Points
- [x] yt-dlp integration working
- [x] Format parser correctly identifying qualities
- [x] Progress bar updating every 3 seconds
- [x] File cached in PostgreSQL (CachedFile table)
- [x] Pyrogram upload successful (up to 4GB)
- [x] Download history recorded

---

## 🎯 TEST SCENARIO 4: Error Handling

### Test Case 4a: Invalid URL
```
User: https://invalid-domain.com/video
Bot Response: ❌ "Invalid URL. Please send a YouTube, Instagram, or TikTok link."
```

### Test Case 4b: Invalid YouTube Link
```
User: https://www.youtube.com/watch?v=invalid_id_that_doesnt_exist
Bot Response: ❌ "Video not found or is private."
```

### Test Case 4c: Age-Restricted Content
```
User: [Age-restricted video URL]
Bot Response: ❌ "This video is age-restricted and requires verification."
```

### Test Case 4d: Download Failure
```
User: [Deleted/unavailable video]
Bot Response: ❌ "Download failed: Video unavailable"
```

### Verification Points
- [x] Error messages are user-friendly
- [x] User is not banned after error
- [x] Download history logs the failure
- [x] Bot recovers gracefully

---

## 🎯 TEST SCENARIO 5: Rate Limiting & Throttle

### Test Steps
1. **Rapid Commands**
   ```
   User sends: /start, /profile, /plans, /history, /referral
   (All within 5 seconds)
   ```

2. **Expected Throttle Response** (after 3rd command)
   ```
   Bot Response: ⏱️ "Slow down! You're sending commands too fast.
                     Try again in 2 seconds."
   ```

3. **Download Spam Test**
   ```
   User sends: [URL] [URL] [URL] [URL] [URL]
   (5 different download requests within 10 seconds)
   ```

4. **Expected Rate Limit** (Free tier: 5 downloads/day)
   ```
   After 5th download:
   Bot Response: 📊 "Daily limit reached. Upgrade to Premium for unlimited downloads."
   ```

### Verification Points
- [x] Throttle middleware blocking rapid commands
- [x] Rate limiting keys in Redis
- [x] User can proceed after cooldown
- [x] Admin can bypass limits

---

## 🎯 TEST SCENARIO 6: Multi-Language Support

### Test Steps
1. **Test Persian**
   ```
   User: /help (after selecting Persian)
   Bot Response: [Persian help message]
   ```

2. **Test English**
   ```
   User: /help (after selecting English)
   Bot Response: [English help message]
   ```

3. **Language Switching**
   ```
   User: /start (again)
   Bot: Remembers previous language preference
   ```

### Verification Points
- [x] Translations loading from locales/fa/messages.json
- [x] Translations loading from locales/en/messages.json
- [x] I18n middleware working
- [x] Language preference persists

---

## 🎯 TEST SCENARIO 7: Admin Commands

### Setup
```
Set ADMIN_IDS=your_telegram_id in .env
```

### Test `/stats` Command
```
Admin: /stats
Bot Response:
👥 Users: 42
📥 Downloads: 156
💰 Revenue: $234.50
📊 Last 24h Growth: +12 users
```

### Test `/broadcast` Command
```
Admin: /broadcast
Bot: "Send the message to broadcast:"
Admin: "Hello everyone! New features coming soon!"
Bot: "Broadcast to 42 users? (confirm)"
Admin: Confirm
Bot: "Broadcasting... ✅ Sent to 42/42 users"
```

### Verification Points
- [x] Admin filter working
- [x] Stats aggregating correctly
- [x] Broadcast FSM working
- [x] Non-admin users cannot access

---

## 🎯 TEST SCENARIO 8: Web Admin Panel

### Setup
```bash
# Terminal 2 - Start web panel
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```

### Test Steps
1. **Access Dashboard**
   ```
   Browser: http://localhost:8000
   ```

2. **Login**
   ```
   Username: admin
   Password: [from .env or default]
   Expected: Redirects to /dashboard
   ```

3. **Test API Endpoint**
   ```bash
   curl http://localhost:8000/api/dashboard/overview
   
   Response:
   {
     "total_users": 42,
     "total_downloads": 156,
     "revenue_usd": 234.50,
     "active_downloads": 3
   }
   ```

4. **Test User Management**
   ```
   GET /api/users/
   Response: List of all users with stats
   
   POST /api/users/{user_id}/ban
   Response: {"status": "banned", "reason": "spam"}
   ```

### Verification Points
- [x] FastAPI serving correctly
- [x] JWT authentication working
- [x] CORS enabled for frontend
- [x] All 20+ endpoints responding

---

## 🎯 TEST SCENARIO 9: Database Persistence

### Test Steps
1. **Create Download Record**
   ```
   Download a YouTube video
   Check database: SELECT * FROM downloads WHERE user_id = 123;
   ```

2. **Verify User Stats**
   ```
   SELECT daily_downloads, coins FROM users WHERE id = 123;
   ```

3. **Check Cache**
   ```
   SELECT * FROM cached_files 
   WHERE url_hash = 'abc123...';
   
   Expected: File cached, ready for re-send
   ```

4. **Verify Subscriptions**
   ```
   SELECT * FROM subscriptions WHERE user_id = 123;
   ```

### Verification Points
- [x] Data persisting to PostgreSQL
- [x] Relationships intact (user → downloads)
- [x] Timestamps accurate
- [x] Cache entries valid

---

## 🎯 TEST SCENARIO 10: Module System (Future Platforms)

### Test Instagram Placeholder
```bash
# (Instagram module not yet implemented)
User: https://www.instagram.com/p/ABC123/
Bot Response: ⚠️ "Instagram downloader coming soon!"
```

### Test TikTok Placeholder
```bash
User: https://www.tiktok.com/@user/video/123456
Bot Response: ⚠️ "TikTok downloader coming soon!"
```

### Verification Points
- [x] Module registry doesn't crash on missing modules
- [x] Graceful error messages
- [x] Ready for module implementation

---

## 🧼 CLEANUP TEST

### After Testing
```bash
# Remove test data
psql -U dlbot_user -d dlbot_db -c "TRUNCATE users, downloads, cached_files CASCADE;"

# Or completely reset
docker stop dlbot-postgres dlbot-redis
docker rm dlbot-postgres dlbot-redis
```

---

## 📊 TEST COVERAGE CHECKLIST

### Bot Functionality
- [ ] /start command
- [ ] Language selection
- [ ] /help command
- [ ] /profile command
- [ ] /plans command
- [ ] /history command
- [ ] /referral command
- [ ] Download flow
- [ ] Quality selection
- [ ] Progress tracking
- [ ] File upload

### Admin Features
- [ ] /admin command (access control)
- [ ] /stats command (statistics)
- [ ] /broadcast command (messaging)
- [ ] /users command (management)

### Error Handling
- [ ] Invalid URLs
- [ ] Network timeouts
- [ ] Rate limiting
- [ ] Throttle protection
- [ ] Age restrictions
- [ ] Deleted videos

### Database
- [ ] User creation
- [ ] Download history
- [ ] Cached files
- [ ] Subscription tracking
- [ ] Stats aggregation

### Services
- [ ] Cache hit/miss
- [ ] User service CRUD
- [ ] Payment tracking
- [ ] Referral system
- [ ] Notification sending

### Web API
- [ ] Dashboard endpoint
- [ ] User management
- [ ] Broadcast API
- [ ] Payment history
- [ ] Settings management

### Security
- [ ] Admin filter
- [ ] Rate limiting
- [ ] Throttle middleware
- [ ] JWT authentication
- [ ] Input validation

---

## 🚨 TROUBLESHOOTING

### Issue: "Bot token not found"
**Solution**: Set BOT_TOKEN in .env file

### Issue: "Cannot connect to database"
**Solution**: Verify PostgreSQL running and credentials correct

### Issue: "Redis connection refused"
**Solution**: Verify Redis running: `redis-cli ping` should return PONG

### Issue: "yt-dlp not working"
**Solution**: Update yt-dlp: `pip install --upgrade yt-dlp`

### Issue: "Pyrogram authentication failed"
**Solution**: Verify APP_ID and APP_HASH from my.telegram.org

---

## 📈 PERFORMANCE METRICS

After testing, check:

```bash
# Database query performance
EXPLAIN ANALYZE SELECT * FROM downloads WHERE user_id = 123;

# Redis cache hit rate
redis-cli INFO stats | grep keyspace_hits

# Download speed (local)
# Should be 2-5 MB/s depending on internet

# API response time
# Should be < 200ms for most endpoints
```

---

## ✅ SIGN-OFF CHECKLIST

When all tests pass:

- [ ] All 61 code validation tests passed
- [ ] Bot startup successful
- [ ] User registration working
- [ ] Download flow complete
- [ ] Error handling graceful
- [ ] Admin commands functional
- [ ] Web API responding
- [ ] Database persisting data
- [ ] Multi-language working
- [ ] No crashes or errors in 1 hour of testing

---

**Testing Started**: [Date]  
**Testing Completed**: [Date]  
**Tester**: [Name]  
**Status**: ⏳ Pending Integration Testing

---

## 📞 Support

For issues, check:
1. `logs/app.log` - Application logs
2. PostgreSQL logs
3. Redis logs
4. Telegram API rate limits
5. Pyrogram session issues

---

**Generated**: 2026-05-23  
**Version**: 1.0.0  
**Phase**: 1 - MVP Testing
