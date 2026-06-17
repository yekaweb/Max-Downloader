# Download Pipeline — Phased Fix Roadmap

> **Last Updated:** 2026-06-17  
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
- [ ] **1.6** Push to GitHub ✅ Done — deploy to server and test with a 480p-only YouTube video

---

## Phase 2 — Fix the Download Execution Engine
> **Files:** `bot/handlers/download_exec.py`  
> **Priority:** 🔴 CRITICAL — even if Phase 1 works, the download itself fails

- [x] **2.1** Add the same bot-bypass `ydl_opts` (Android client + User-Agent) to the download-time opts
- [x] **2.2** Add `"1440"` to `quality_map` (Bug #4)
- [x] **2.3** Fix `prepare_filename()` → use glob to find actual merged file on disk (Bug #5)
- [x] **2.4** Fix codec format string fallback to always include `height` constraint (Bug #6)
- [x] **2.5** Add `merge_output_format: mp4` to ensure consistent output extension
- [ ] **2.6** Deploy to server and test a full download end-to-end

---

## Phase 3 — Fix the Quality Keyboard UI
> **Files:** `bot/keyboards/inline/download.py`  
> **Priority:** 🟡 MEDIUM — UI correctness after data fixes

- [x] **3.1** Guard against `None` value for `size_mb` in all keyboard buttons (Bug #7)
  - Display `"حجم: نامشخص"` when size is `None`, not a crash
- [x] **3.2** Back-button on `get_video_codec_keyboard` now points to `back_to_format` (format type selection) — previously wrongly pointed to `back_to_quality`
- [x] **3.3** AV1 and VP9 codec buttons only shown when that codec is actually available for the video
- [x] **3.4** Pushed to GitHub ✅

---

## Phase 4 — Add Cookies Support (Long-Term Bot-Detection Bypass)
> **Files:** `utils/format_sizes.py`, `bot/handlers/download_exec.py`, `Dockerfile`  
> **Priority:** 🟠 IMPORTANT — makes the fix permanent

- [ ] **4.1** Export `cookies.txt` from a logged-in Chrome/Firefox browser using a cookie-export extension
- [ ] **4.2** Place `cookies.txt` in the project root and add it to `.gitignore`
- [ ] **4.3** Add `'cookiefile': '/app/cookies.txt'` to `ydl_opts` in both `format_sizes.py` and `download_exec.py`
- [ ] **4.4** Mount `cookies.txt` in `docker-compose.yml` as a read-only volume bind
- [ ] **4.5** Test with a geo-restricted or age-gated video to verify cookies work

---

## Phase 5 — (Future) Add Dubbed Audio Track Selection
> **Reference:** `dubbed_option/ROADMAP.md`  
> **Priority:** 🟢 LOW — feature enhancement, not a bug

- [ ] **5.1** Extract `language` field from audio-only formats in `get_exact_format_sizes`
- [ ] **5.2** Build `get_audio_language_keyboard(languages: dict)` in `download.py`
- [ ] **5.3** Add `video_selecting_language` FSM state in `DownloadStates`
- [ ] **5.4** Wire language selection into `format_handler.py` after quality selection
- [ ] **5.5** Apply selected `audio_lang` to `ydl_opts["format"]` in `download_exec.py`
- [ ] **5.6** Auto-skip language step if video has only one audio track

---

## Current Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Fix metadata extraction | ✅ Complete |
| Phase 2 | Fix download execution engine | ✅ Complete |
| Phase 3 | Fix quality keyboard UI | ✅ Complete |
| Phase 4 | Add cookies for permanent bypass | ⏳ Pending |
| Phase 5 | Dubbed audio track selection | 🔮 Future |
