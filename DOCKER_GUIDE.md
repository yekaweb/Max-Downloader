# 🐳 اجرای ربات با Docker

**۲ روش وجود دارد:**

---

## 🎯 روش ۱: Docker Compose (توصیه شده)

### مزایا:
✅ PostgreSQL و Redis خودکار شروع می‌شوند  
✅ تمام سرویس‌ها با هم کار می‌کنند  
✅ ۱ دستور و تمام!

### مراحل:

#### **۱. Docker Desktop را باز کنید**
- Windows: بحث و جستجو `Docker Desktop`
- باز کنید و صبر کنید تا کاملاً شروع شود

#### **۲. Terminal را باز کنید** (VS Code)
```
Ctrl + ~
```

#### **۳. دستور Docker Compose:**
```bash
docker-compose up -d
```

**نتیجه:**
```
✅ Creating dlbot_postgres ... done
✅ Creating dlbot_redis ... done
✅ Creating dlbot_bot ... done
```

#### **۴. ربات شروع می‌شود**
```bash
docker-compose logs -f dlbot
```

**نتیجه:**
```
Bot started successfully!
Listening for messages...
```

---

## 🎯 روش ۲: Docker بدون Compose

### اگر فقط ربات می‌خواهید:

```bash
# Build Image
docker build -t dlbot .

# اجرا
docker run -d \
  --name dlbot \
  -e BOT_TOKEN=8603008659:AAH1UaVOCJpE3heq8CdUtGffvSJFuDI53Ao \
  -e PYROGRAM_APP_ID=38449735 \
  -e PYROGRAM_APP_HASH=30c6936b37f0767f3c3f128df9b2ca00 \
  dlbot
```

---

## 📋 دستورات مفید Docker:

### مشاهده لاگ‌ها:
```bash
docker-compose logs -f dlbot
```

### متوقف کردن:
```bash
docker-compose down
```

### پاک کردن کامل:
```bash
docker-compose down -v
```

### راه‌اندازی دوباره:
```bash
docker-compose restart
```

### وضعیت کنتینرها:
```bash
docker-compose ps
```

---

## ⚙️ فایل‌های Docker:

| فایل | استفاده |
|------|---------|
| `Dockerfile` | نحوه ساخت Image |
| `docker-compose.yml` | تمام سرویس‌ها (Bot, DB, Redis) |

---

## 🚀 **خلاصه برای شروع:**

1. **Docker Desktop را باز کنید**
2. **Terminal را باز کنید**
3. **یک دستور:**
```bash
docker-compose up -d
```

**تمام!** ربات شروع می‌شود! 🎉

---

## ❌ مشکل؟

### Docker نصب نیست:
```
docker: command not found
```
**حل**: Docker Desktop را نصب کنید (docker.com)

### Port اشغال است:
```
Error: Port 5432 is in use
```
**حل**: دستور:
```bash
docker-compose down
docker-compose up -d
```

### Compose نصب نیست:
```bash
pip install docker-compose
```

---

## 📊 معماری Docker Compose:

```
┌─────────────┐
│   ربات      │ ← Telegram Bot
├─────────────┤
│ PostgreSQL  │ ← دیتابیس
├─────────────┤
│   Redis     │ ← کش
├─────────────┤
│   Celery    │ ← تسک‌های Async
└─────────────┘
```

**تمام اینها با ۱ دستور شروع می‌شوند!** 🚀

---

**نوشته شده برای Docker with ❤️**
