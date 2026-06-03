# 🔧 DLBot - Installation & Troubleshooting Guide

## ❌ مشکلات رو قبلاً مشاهده کردیم

### 1. **Dependency Error: asyncio-contextmanager==1.0.0**
**مشکل:** نسخه دقیق وجود ندارد
```
ERROR: Could not find a version that satisfies the requirement asyncio-contextmanager==1.0.0
```

**✅ حل:** تغییر به نسخه موجود
```bash
# در requirements.txt:
asyncio-contextmanager==1.0.1  # بجای 1.0.0
```

---

## 🎯 صحیح Installation Guide

### مرحله 1: بررسی Python نسخه
```bash
python --version
# باید 3.11+ باشد، ترجیحاً 3.12
```

### مرحله 2: Virtual Environment
```bash
# Create
python -m venv venv

# Activate - Windows:
venv\Scripts\activate

# Activate - Linux/Mac:
source venv/bin/activate
```

### مرحله 3: Dependencies Install
```bash
# اطمینان از pip بروز
python -m pip install --upgrade pip

# نصب requirements
pip install -r requirements.txt

# اگر مشکل داشت، یکی یکی نصب کن:
pip install aiogram==3.4.1
pip install pyrogram==2.0.106
pip install TgCrypto==1.2.5
# ... و غیره
```

### مرحله 4: Environment Setup
```bash
# Copy example env
cp .env.example .env  # Windows/Mac
# یا
Copy-Item .env.example .env  # PowerShell

# Edit .env with your credentials
# - BOT_TOKEN
# - Database credentials
# - Pyrogram APP_ID & APP_HASH
```

### مرحله 5: Database Initialization
```bash
# Create directory structure
python init_project.py

# Run migrations
alembic upgrade head
```

---

## ▶️ Running the Project

### Start Bot (Terminal 1)
```bash
python main.py
```

### Start Web Panel (Terminal 2)
```bash
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```

### Alternative: Docker
```bash
docker-compose up -d
```

---

## 🐛 Common Issues & Fixes

### Issue 1: PowerShell `&&` syntax error
**Problem:** `python init.py && alembic upgrade head` fails

**Solution:** Use `;` instead or run separately:
```powershell
# Option 1: Semicolon separator
python init_project.py ; alembic upgrade head

# Option 2: Separate commands
python init_project.py
alembic upgrade head

# Option 3: Use CMD instead of PowerShell
cmd /c "python init_project.py && alembic upgrade head"
```

### Issue 2: Module not found (loguru, uvicorn, etc.)
**Problem:** 
```
ModuleNotFoundError: No module named 'loguru'
```

**Solution:** Verify installation
```bash
# Check if venv is activated
where python  # or 'which python' on Linux

# Re-install requirements
pip install -r requirements.txt --upgrade

# Or install individually
pip install loguru uvicorn fastapi
```

### Issue 3: PostgreSQL connection failed
**Problem:** Database connection refused

**Solution:**
```bash
# Verify PostgreSQL is running
# Windows: Check Services app
# Linux: sudo systemctl status postgresql
# Mac: brew services list | grep postgres

# Test connection
psql -U postgres -d postgres -c "SELECT 1"
```

### Issue 4: Redis connection failed
**Problem:** Redis connection refused

**Solution:**
```bash
# Start Redis locally or via Docker
docker run -d -p 6379:6379 redis:7
```

### Issue 5: Pyrogram TgCrypto build fails
**Problem:** `Building wheel for TgCrypto failed`

**Solution:**
```bash
# Install build tools
pip install --upgrade pip setuptools wheel

# Then retry
pip install TgCrypto==1.2.5 --force-reinstall --no-cache-dir
```

---

## 📋 Complete Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created & activated
- [ ] requirements.txt installed successfully
- [ ] .env file created with credentials
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] Database initialized (`alembic upgrade head`)
- [ ] Bot started (`python main.py`)
- [ ] Web panel accessible (`http://localhost:8000`)

---

## 🧪 Testing Installation

### Test 1: Import modules
```bash
python -c "from modules.youtube import YouTubeDownloader; print('✅ YouTube module OK')"
python -c "from services.file_service import FileService; print('✅ File service OK')"
python -c "from utils.progress import ProgressBar; print('✅ Progress bar OK')"
```

### Test 2: Run bot test
```bash
python test_youtube_module.py
```

### Test 3: Check web panel
```bash
# Try health endpoint
curl http://localhost:8000/health
# Should return: {"status":"ok","version":"1.0.0",...}
```

---

## 📞 Support Files

- `README.md` - Project overview
- `ROADMAP.md` - Feature checklist
- `IMPLEMENTATION_COMPLETE.md` - Detailed completion report
- `.env.example` - Environment variables template

---

## 🚀 Next Steps

1. ✅ Fix requirements.txt (asyncio-contextmanager==1.0.1)
2. ✅ Fresh install in clean venv
3. ✅ Configure .env
4. ✅ Initialize database
5. ✅ Start bot & web panel
6. ✅ Test all features
7. ⏳ End-to-end FSM testing (final phase)

---

**Status:** Ready for deployment after testing ✨
