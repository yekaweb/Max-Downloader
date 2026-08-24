# Download Pipeline — Phased Fix Roadmap

> **Last Updated:** 2026-06-17 — ALL PHASES COMPLETE ✅  
> This file is updated after every fix. Completed phases are marked `[x]`.

---

## Phase 1 — Fix Metadata Extraction (Root Cause)
> **Files:** `utils/format_sizes.py`  
> **Priority:** 🔴 CRITICAL — nothing else works until this is fixed

- [x] **1.1** Replace `asyncio.get_event_loop()` with `asyncio.get_running_loop()` (Bug #2)
- [x] **1.2** Add Android `player_client` + spoofed mobile User-Agent to bypass YouTube bot-detection (Bug #1)
- [x] **1.3** Add `noplaylist=True`, `socket_timeout=30` to `ydl_opts`
- [x] **1.4** Remove the `filesize` gate (`if height and filesize`) — include formats even when filesize is `None` (Bug #3)
- [x] **1.5** In result-building loop, gracefully handle `size_mb=None` (output `None` instead of crashing)
- [x] **1.6** Pushed to GitHub ✅ — deploy to server and test with a 480p-only YouTube video

---

## Phase 2 — Fix the Download Execution Engine
> **Files:** `bot/handlers/download_exec.py`  
> **Priority:** 🔴 CRITICAL — even if Phase 1 works, the download itself fails

- [x] **2.1** Add the same bot-bypass `ydl_opts` (Android client + User-Agent) to the download-time opts
- [x] **2.2** Add `"1440"` to `quality_map` (Bug #4)
- [x] **2.3** Fix `prepare_filename()` → use glob to find actual merged file on disk (Bug #5)
- [x] **2.4** Fix codec format string fallback to always include `height` constraint (Bug #6)
- [x] **2.5** Add `merge_output_format: mp4` to ensure consistent output extension
- [x] **2.6** Pushed to GitHub ✅

---

## Phase 3 — Fix the Quality Keyboard UI
> **Files:** `bot/keyboards/inline/download.py`  
> **Priority:** 🟡 MEDIUM — UI correctness after data fixes

- [x] **3.1** Guard against `None` value for `size_mb` in all keyboard buttons (Bug #7)
  - Display `"حجم: نامشخص"` when size is `None`, not a crash
- [x] **3.2** Back-button on `get_video_codec_keyboard` now points to `back_to_format` (format type selection)
- [x] **3.3** AV1 and VP9 codec buttons only shown when that codec is actually available for the video
- [x] **3.4** Pushed to GitHub ✅

---

## Phase 4 — Add Cookies Support (Long-Term Bot-Detection Bypass)
> **Files:** `utils/format_sizes.py`, `docker-compose.yml`, `.gitignore`  
> **Priority:** 🟠 IMPORTANT — makes the fix permanent

- [x] **4.1** Added `_build_ydl_opts()` factory function that auto-injects `cookiefile` if `/app/cookies.txt` exists
- [x] **4.2** Added `cookies.txt` to `.gitignore` — token-sensitive file must NOT be committed
- [x] **4.3** `'cookiefile': '/app/cookies.txt'` injected automatically in both `format_sizes.py` and `download_exec.py` via shared `_build_ydl_opts()`
- [x] **4.4** Added `./cookies.txt:/app/cookies.txt:ro` bind-mount to `dlbot` and `celery_worker` in `docker-compose.yml`
- [ ] **4.5** ⚠️ **ACTION REQUIRED (Manual):** Export `cookies.txt` from a logged-in Chrome browser:
  1. Install the extension **"Get cookies.txt LOCALLY"** in Chrome
  2. Go to `https://www.youtube.com` while logged in
  3. Click the extension → Export → Save as `cookies.txt`
  4. Upload `cookies.txt` to your server in the `/root/Max-Downloader/` directory
  5. Run `sudo docker compose up -d --build` to apply

---

## Phase 5 — Dubbed Audio Track Selection
> **Files:** `utils/format_sizes.py`, `bot/keyboards/inline/download.py`, `bot/states/download.py`, `bot/handlers/format_handler.py`, `bot/handlers/download_exec.py`  
> **Priority:** ✅ COMPLETE

- [x] **5.1** Extract `language` field from audio-only formats in `get_exact_format_sizes`
  - Returns `dubbed_tracks` dict only when more than 1 language track exists
  - Includes language display names (English 🇺🇸, فارسی 🇮🇷, etc.)
- [x] **5.2** Built `get_dubbed_language_keyboard(dubbed_tracks: dict)` in `download.py`
  - Includes "صدای اصلی ویدیو (پیش‌فرض)" button for original audio
  - Shows file size of each track when available
- [x] **5.3** Added `video_selecting_language` FSM state to `DownloadStates`
- [x] **5.4** Wired language step into `format_handler.py` between subtitle → send_as
  - `select_subtitle` now checks for `dubbed_tracks` and routes to language step if >1 track
- [x] **5.5** Applied `audio_lang` to `ydl_opts["format"]` in `download_exec.py`
  - Uses `bestaudio[language=xx]/bestaudio` selector when a specific lang is selected
- [x] **5.6** Auto-skip implemented: language step is skipped entirely when video has ≤1 audio language track
- [x] **5.7** Pushed to GitHub ✅

---

## Current Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Fix metadata extraction | ✅ Complete |
| Phase 2 | Fix download execution engine | ✅ Complete |
| Phase 3 | Fix quality keyboard UI | ✅ Complete |
| Phase 4 | Add cookies for permanent bypass | ✅ Code Complete — needs manual cookies.txt |
| Phase 5 | Dubbed audio track selection | ✅ Complete |

---

## 🚀 Deployment Checklist (Server Commands)

```bash
# 1. Pull the latest code
git fetch --all && git reset --hard origin/main

# 2. Rebuild and restart all containers
sudo docker compose up -d --build

# 3. Check bot logs
sudo docker logs dlbot_bot --tail 30

# 4. (Optional, for cookies) Upload cookies.txt manually then restart
# scp cookies.txt user@212.87.198.89:/root/Max-Downloader/cookies.txt
sudo docker compose restart dlbot_bot dlbot_celery_worker
```
