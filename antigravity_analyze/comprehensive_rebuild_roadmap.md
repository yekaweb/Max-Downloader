# 🗺️ Comprehensive Project Rebuild Roadmap (DLBot)

**Status:** 🛠️ In Progress
**Reference:** Based on `first_analyze.md`, `00_MASTER_ROADMAP.md`, and `SPRINT_1_cleanup.md`

---

## 📌 Roadmap Legend

- `[ ]` : Pending (Not started)
- `[/]` : In Progress
- `[x]` : Completed
- `🔴` : Critical Priority (Must be fixed for basic stability)
- `🟡` : Important Priority (Required for MVP/Commercial release)
- `🟢` : Medium Priority (Enhancements & Polish)

---

## 🚩 Phase 1: Critical Cleanup & Foundation (Sprint 1)

**Goal:** Eliminate technical debt and establish a professional architecture.

### 1.1 Dead Code & Garbage Removal 🔴

- [x] Delete redundant loaders (`loader_simple.py`, `loader_complete.py`, etc.) | *Ref: first_analyze Weakness 1*
- [x] Delete garbage files (`.ipynb`, `.txt` reports, backup models) | *Ref: first_analyze Weakness 2*
- [x] Unify keyboards (Merge `bot/keyboards.py` into `bot/keyboards/inline/`)

### 1.2 Architecture Refactoring 🔴

- [x] **Split the God File:** Extract `bot/loader_professional_enhanced.py` into:
  - [x] `bot/handlers/start.py`
  - [x] `bot/handlers/url_handler.py`
  - [x] `bot/handlers/format_handler.py`
  - [x] `bot/handlers/download_exec.py`
  - [x] `bot/handlers/cache_handler.py`
- [x] Activate modular download routing with new handler modules (`url_handler.py`, `format_handler.py`, `cache_handler.py`)
- [x] Create a clean `bot/loader.py` (Initialization only)
- [x] Rewrite `main.py` as a clean entry point

### 1.3 Configuration & State Management 🔴

- [x] Rewrite `config.py` using **Pydantic v2** (Strict validation) | *Ref: first_analyze Weakness 3*
- [x] Switch FSM from `MemoryStorage` to `RedisStorage` (Redis fallback support implemented in `bot/loader.py`) | *Ref: first_analyze Weakness 9*
- [x] Setup **Alembic** for database migrations (Initial env present, migration scripts still pending) | *Ref: first_analyze Weakness 13*

---

## 🚩 Phase 2: Core Logic & Stability (Sprint 2)

**Goal:** Fix the broken core features and ensure the bot actually works as promised.

### 2.1 Download Engine Fixes 🔴

- [x] **Fix Quality Passthrough:** Ensure user-selected quality/codec is passed to `yt-dlp` | *Ref: first_analyze Weakness 4*
- [x] Implement **Pyrogram** for large file uploads (up to 4GB) | *Ref: We want build this.md*
- [x] Fix **Progress Tracking:** Implement real speed, ETA, and MB calculations | *Ref: first_analyze Weakness 14*
- [x] Implement **Complete File Cleanup:** Ensure all temp files (original + compressed) are deleted | *Ref: first_analyze Weakness 18*

### 2.2 Stability & Error Handling 🔴

- [x] Replace generic `except Exception` with categorized error handling | *Ref: first_analyze Weakness 15*
- [x] Fix **Bot Session Leak** in `phases_integration.py` | *Ref: first_analyze Weakness 17*
- [x] Implement **Retry Logic** for failed downloads

---

## 🚩 Phase 3: MVP Features & User Experience (Sprint 3)

**Goal:** Complete the basic feature set for a viable product.

### 3.1 Platform Expansion 🟡

- [x] **TikTok Module:** Implement `modules/tiktok/` using `yt-dlp` | *Ref: first_analyze Weakness 7*
- [x] **Instagram Stability:** Implement session management and rate limiting | *Ref: first_analyze Weakness 8*
- [x] **Twitter Normalization:** Fix fragile URL resolution | *Ref: first_analyze Weakness 19*

### 3.2 User Experience & i18n 🟡

- [ ] **Real i18n:** Remove all hardcoded strings and move to `locales/*.json` | *Ref: first_analyze Weakness 11*
- [x] Implement **Rate Limiting** per user via Redis | *Ref: first_analyze Weakness 22*
- [x] Implement **Force-Join** middleware (Async validation)

---

## 🚩 Phase 4: Monetization & Business Logic (Sprint 4)

**Goal:** Turn the bot into a business with real payments and limits.

### 4.1 Payment Integration 🔴

- [x] Implement **CryptoBot** (Telegram native) | *Ref: first_analyze Weakness 5*
- [x] Implement **ZarinPal** (IRR payment)
- [x] Implement **NOWPayments** (Global crypto)
- [x] Create real webhook handlers for payment confirmation

### 4.2 Subscription Enforcement 🔴

- [x] Implement **Plan Limits** (Daily download limit, max file size) | *Ref: first_analyze Weakness 6*
- [x] Link payment success to automatic plan activation
- [x] Implement **Referral Logic** (Coins $\rightarrow$ Plan upgrade) | *Ref: first_analyze Weakness 21*

---

## 🚩 Phase 5: Advanced Features & Admin (Sprint 5)

**Goal:** Add professional management tools and advanced capabilities.

### 5.1 Admin Panel 🟡

- [x] Connect **FastAPI Web Panel** to the actual database
- [x] Implement **Broadcast System** (Mass messaging with rate limits)
- [x] User management (Ban/Unban/Upgrade) via Web UI

### 5.2 Advanced Services 🟢

- [x] Implement **Celery** for background task queueing | *Ref: first_analyze Weakness 20*
- [x] Implement **Adaptive Compression** based on device/connection

---

## 🚩 Phase 6: Production Readiness (Sprint 6)

**Goal:** Ensure the bot is stable, tested, and ready for 100k users.

### 6.1 Quality Assurance 🔴

- [x] Implement **Pytest** coverage for all critical paths (Happy paths) | *Ref: first_analyze Weakness 10*
- [x] Perform **Load Testing** for concurrent downloads
- [x] Security audit (Remove stack traces from user messages)

### 6.2 Deployment & Monitoring 🟢

- [x] Optimize `docker-compose.yml` for production
- [x] Setup **Loguru** rotation and centralized logging
- [x] Implement health checks for Redis/Postgres
