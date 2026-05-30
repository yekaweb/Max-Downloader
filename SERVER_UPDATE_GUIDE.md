# 🔧 دستورات برای بهبود ربات روی سرور

## 1. متصل شو به سرور

```bash
ssh root@turkeyserver
```

## 2. خاموش کردن ربات

```bash
tmux kill-session -t dlbot
```

## 3. دانلود فایل‌های بهبود

```bash
cd /home/dlbot-telegram
git pull
```

## 4. شروع مجدد ربات

```bash
tmux new-session -d -s dlbot "python3 main.py"
```

## 5. بررسی لاگ

```bash
tail -f logs/dlbot.log
```

باید ببینی:
```
INFO | 🤖 Starting DLBot
INFO | 🚀 Starting bot polling...
INFO | 📡 Bot is listening for updates...
```

## 6. تست روی Telegram

- دستور `/start` بفرست
- دکمه‌های جدید رو ببینی
- دستور `/download` بفرست
