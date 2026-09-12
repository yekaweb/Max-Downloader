# 🗺️ Master Project Roadmap: Titan Downloader Mesh (Max-Downloader v2.0)

> **Standard**: `project-roadmap-manager` v2.0  
> **Status Indicators**: ⬜ Not Started | 🟨 In Progress | 🟩 Completed | ⏸ Waiting | ❌ Blocked  
> **Architecture Target**: Unblockable 4-Tier Waterfall YouTube & Multi-Platform Telegram Bot  

---

## 📊 Global Project Overview & Progress

```text
[🟩 Phase 1: Zero-Failure Immediate Bypass] --------> 🟩 Completed (100%)
[🟩 Phase 2: PO-Token & Cobalt Fallback] -----------> 🟩 Completed (100%)
[🟩 Phase 3: Crowdsourced Gmail Passkey Pool] -------> 🟩 Completed (100%)
[🟩 Phase 4: AI Studio - Persian Voice Dubbing] -----> 🟩 Completed (100%)
```

---

## 🚀 Phase 1: Immediate YouTube Bypass Engine (Zero-Failure Quick Fix)
- **Purpose**: Restore 100% working YouTube downloads on the live bot immediately using client spoofing, headers, and cookie integration.
- **Complexity**: Low-Medium
- **Dependencies**: `yt-dlp >= 2026.08`
- **Definition of Done**: Bot successfully downloads YouTube 1080p, 720p, and MP3 audio from datacenter IP without 429/Sign-in errors.
- **Status**: 🟩 Completed

### 📦 Module 1.1: yt-dlp Configuration & Cookie Integration
- **Purpose**: Pass `cookies.txt` and anti-ban settings to all yt-dlp invocations.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 1.1.1: Updated `modules/youtube/config.py` with dynamic `cookiefile` path and anti-bot extractor arguments.
  - [x] 🟩 Subtask 1.1.2: Updated `bot/handlers/download_exec.py` to inject `cookiefile: cookies.txt` and anti-bot headers.
  - [x] 🟩 Subtask 1.1.3: Updated `utils/format_sizes.py` to resolve absolute path for `cookies.txt`.

### 📦 Module 1.2: Player Client Spoofing (Android / iOS / Safari / MWeb)
- **Purpose**: Bypass YouTube Web BotGuard VM by pretending to be official mobile client apps.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 1.2.1: Added `extractor_args: {'youtube': {'player_client': ['android', 'web_safari', 'mweb', 'ios'], 'lang': ['en', 'fa']}}`.
  - [x] 🟩 Subtask 1.2.2: Added realistic User-Agents and HTTP navigation headers.
  - [x] 🟩 Subtask 1.2.3: Configured 10 retries and fragment recovery options.

### 📦 Module 1.3: Verification Gate & Live Test
- **Purpose**: Deterministically verify YouTube downloads across video and audio formats.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 1.3.1: Verified CLI format extraction and actual video download on YouTube links (100% success).
  - [x] 🟩 Subtask 1.3.2: Verified 26 unit tests passing with zero regressions.
  - [x] 🟩 Subtask 1.3.3: Restarted live bot daemon on the server.

---

## 🛡️ Phase 2: Local PO-Token Microservice & Cobalt API Fallback
- **Purpose**: Ensure long-term resilience against Google cipher changes with automated PO-Token generation and a multi-engine waterfall fallback.
- **Complexity**: Medium
- **Dependencies**: `services/potoken_service.py`, `services/cobalt_service.py`, `services/waterfall_download_service.py`
- **Definition of Done**: Bot seamlessly falls back to Cobalt or PO-Token if yt-dlp encounters a temporary restriction.
- **Status**: 🟩 Completed

### 📦 Module 2.1: Local PO-Token Service
- **Purpose**: Manage and inject valid `visitorData` and `poToken` into yt-dlp extractor options.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 2.1.1: Created `services/potoken_service.py` with dynamic caching and injection.
  - [x] 🟩 Subtask 2.1.2: Connected PO-Token provider to yt-dlp extractor options.

### 📦 Module 2.2: Cobalt API & Waterfall Fallback
- **Purpose**: Multi-instance secondary download engine if yt-dlp fails.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 2.2.1: Created `services/cobalt_service.py` with multi-instance cluster rotation.
  - [x] 🟩 Subtask 2.2.2: Created `services/waterfall_download_service.py` (Tier 1: yt-dlp -> Tier 2: Cobalt -> Tier 3: Direct).
  - [x] 🟩 Subtask 2.2.3: Hooked Waterfall fallback into `bot/handlers/download_exec.py`.

---

## 🎁 Phase 3: Crowdsourced Gmail Donation Pool & Passkey System (Rostam Model)
- **Purpose**: Scale to hundreds of Google accounts for free by granting VIP tiers in exchange for user-donated idle Gmails.
- **Complexity**: High
- **Dependencies**: SQLAlchemy, Playwright Stealth, AccountPoolService
- **Definition of Done**: Users donate Gmails with Passkey via `/donate`, receive automated VIP, and cookies auto-refresh.
- **Status**: 🟩 Completed

### 📦 Module 3.1: Account Pool Database & Models
- **Purpose**: Store and manage multi-account state and health.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 3.1.1: Created `database/models/google_account_pool.py` and exported in models.
  - [x] 🟩 Subtask 3.1.2: Implemented `database/repositories/google_account_repo.py` for load balancing & usage tracking.
  - [x] 🟩 Subtask 3.1.3: Implemented `services/account_pool_service.py` with VIP tiers (سپهبد, اسفندیار, رستم).

### 📦 Module 3.2: Telegram Bot Donation Flow
- **Purpose**: User-facing UI for donating accounts and receiving VIP.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 3.2.1: Built `bot/handlers/donation.py` with `/donate` command and FSM flow.
  - [x] 🟩 Subtask 3.2.2: Integrated VIP Donation buttons in main reply keyboard (`bot/handlers/start.py` & `bot/handlers/menu.py`).
  - [x] 🟩 Subtask 3.2.3: Registered `donation_router` in `bot/handlers/__init__.py`.

### 📦 Module 3.3: Playwright & Automated Cookie Refresher
- **Purpose**: Background daemon to simulate human activity and refresh session cookies.
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 3.3.1: Installed Playwright engine.
  - [x] 🟩 Subtask 3.3.2: Created `scripts/refresh_cookies.py` for automated synchronization.

---

## 🤖 Phase 4: AI Studio - Persian Neural Voice Dubbing
- **Purpose**: Transform the bot into an AI media portal with Persian neural voice dubbing and smart features.
- **Complexity**: Medium-High
- **Dependencies**: Edge-TTS Neural Voices (`fa-IR-FaridNeural`, `fa-IR-DilaraNeural`), FFmpeg
- **Definition of Done**: High-quality Persian voice synthesis and video audio track ducking/mixing.
- **Status**: 🟩 Completed

### 📦 Module 4.1: Neural Persian Vocal Synthesis
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 4.1.1: Created `services/ai_dubbing_service.py` using Microsoft Neural Persian voices.
  - [x] 🟩 Subtask 4.1.2: Added support for Male (`fa-IR-FaridNeural`) and Female (`fa-IR-DilaraNeural`) voices.

### 📦 Module 4.2: Vocal Synthesis & FFmpeg Audio Ducking
- **Status**: 🟩 Completed
  - [x] 🟩 Subtask 4.2.1: Implemented async FFmpeg background ducking (`amix` filter).
  - [x] 🟩 Subtask 4.2.2: Stream copy video track for ultra-fast generation.
