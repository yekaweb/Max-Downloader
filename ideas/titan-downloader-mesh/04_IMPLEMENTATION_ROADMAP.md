# 04. Implementation Roadmap: Titan Downloader Mesh

## 🏁 Phased Execution Matrix

### ⚡ Phase 1: Zero-Failure Immediate Engine Fix (Immediate - Day 1)
- [ ] Connect `cookies.txt` directly to `yt-dlp` in `bot/handlers/download_exec.py` and `modules/youtube/downloader.py`.
- [ ] Configure `player_client: ['android', 'ios', 'tv_embedded', 'web_safari']` in `extractor_args`.
- [ ] Add real-world desktop/mobile User-Agents and TLS cipher options.
- [ ] Verify instant YouTube 1080p/720p/Audio downloads on the live Telegram bot.

---

### 🛡️ Phase 2: Local PO-Token Daemon & Cobalt Fallback (Days 2-3)
- [ ] Deploy lightweight `bg-utils` PO-Token microservice on `localhost:4444`.
- [ ] Deploy self-hosted `imputnet/cobalt` instance as instant Tier-3 fallback engine.
- [ ] Implement automatic waterfall error handler in `DownloadService`.

---

### 🎁 Phase 3: The Crowdsourced Gmail Pool & Passkey VIP System (Days 4-6)
- [ ] Create `CookiePoolManager` with SQLite persistence for multiple Google accounts.
- [ ] Add `/donate` command in Telegram bot:
  - 1 Gmail = 1 Month VIP (سپهبد)
  - 3 Gmails = 6 Months VIP (اسفندیار)
  - 5 Gmails = Permanent Lifetime VIP (رستم)
- [ ] Automated Playwright stealth background worker to refresh cookies every 12 hours.

---

### 🤖 Phase 4: AI Voice Dubbing & Chapter Highlights (Week 2+)
- [ ] OpenAI Whisper async audio transcription worker.
- [ ] Edge-TTS / ElevenLabs Persian neural voice synthesizer.
- [ ] Inline button: "🇮🇷 دریافت دوبله فارسی با هوش مصنوعی".

---

## 🎯 Immediate Action Item (First Hour)
Patch `bot/handlers/download_exec.py` and `modules/youtube/config.py` with `cookiefile` and `player_client` spoofing to get YouTube downloads working immediately on the live bot.
