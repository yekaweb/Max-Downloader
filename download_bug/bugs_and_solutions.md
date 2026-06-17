# Download Pipeline — Bugs & Solutions

> **Analysis Date:** 2026-06-17  
> **Scope:** Full download flow from URL submission → metadata extraction → quality buttons → actual download

---

## Bug #1 — Silent Exception Swallowing in `get_exact_format_sizes` (CRITICAL)

### Location
`utils/format_sizes.py` — lines 32–134

### Description
The entire `try/except` block in `get_exact_format_sizes()` catches **all exceptions** and returns a plain empty dict `{}`, or now `{"error": str(e)}`. However, the biggest problem is deeper: **the function itself never had any mechanisms to handle YouTube's bot-detection**. On datacenter IPs (like the Turkey VPS), YouTube returns HTTP 429 or a "Sign in to confirm you're not a bot" response. `yt-dlp` raises a `DownloadError` in this case, which is swallowed silently and returns `{}`.

The result: the `format_info` dict is empty, the keyboard shows nothing useful, and the user is stuck.

### Technical Root Cause
```python
# ❌ BEFORE: No bot-detection countermeasures
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,
}
```

YouTube actively fingerprints requests from server IPs. Without a real User-Agent and cookies, any datacenter request will be rejected.

### Solution
Add a spoofed browser `User-Agent` header, set `extractor_args` to use the `android` client (which bypasses most bot checks), and set a reasonable `socket_timeout`. Also add `noplaylist=True` to avoid playlist expansion.

```python
# ✅ FIXED: ydl_opts in get_exact_format_sizes
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,
    'noplaylist': True,
    'socket_timeout': 30,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    },
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/90.0.4430.91 Mobile Safari/537.36'
        ),
    },
}
```

---

## Bug #2 — `asyncio.get_event_loop()` Deprecation Warning (MEDIUM)

### Location
`utils/format_sizes.py` — line 44

### Description
`asyncio.get_event_loop()` is deprecated in Python 3.10+ and **will raise a DeprecationWarning or even fail** in Python 3.12 if there is no current running event loop. The correct pattern is `asyncio.get_running_loop()` inside an `async` function.

```python
# ❌ BEFORE
loop = asyncio.get_event_loop()
info = await loop.run_in_executor(
    None,
    lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
)

# ✅ AFTER
loop = asyncio.get_running_loop()
info = await loop.run_in_executor(
    None,
    lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
)
```

---

## Bug #3 — Video-Only Formats Excluded Because `filesize` is `0` or `None` (CRITICAL)

### Location
`utils/format_sizes.py` — lines 66–81

### Description
The current logic requires **both** `height` and `filesize` to be non-zero:

```python
if height and filesize:  # ❌ Skips valid formats that have no filesize
```

YouTube very often does **not** provide `filesize` or `filesize_approx` for video-only DASH streams. The field is `None` or `0`. This means an entire 480p-only video where the filesize is `None` will have **zero entries** in `video_by_height`, resulting in an empty `video_formats` dict — which is the direct cause of the "hallucinated quality" issue showing up when the fallback keyboard was used.

### Solution
Remove the `filesize` gate. Still try to compute size, but allow the format to be included even when size is unknown:

```python
# ✅ FIXED
for fmt in formats:
    if fmt.get('vcodec') not in (None, 'none') and fmt.get('vcodec'):
        height = fmt.get('height', 0)
        if not height:
            continue
        filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
        vcodec = fmt.get('vcodec', 'unknown').split('.')[0]
        
        if height not in video_by_height:
            video_by_height[height] = []
        video_by_height[height].append({
            'filesize': filesize,   # May be 0; that is OK now
            'vcodec': vcodec,
            'format_id': fmt.get('format_id'),
            'ext': fmt.get('ext'),
        })
```

And in the result-building block, handle zero filesize gracefully:

```python
# ✅ FIXED
for height, label in height_labels.items():
    if height in video_by_height:
        fmts = video_by_height[height]
        # Prefer formats with known size; fall back to first
        fmts_with_size = [f for f in fmts if f['filesize'] > 0]
        best_fmt = min(fmts_with_size, key=lambda x: x['filesize']) if fmts_with_size else fmts[0]
        size_mb = round(best_fmt['filesize'] / (1024 * 1024), 1) if best_fmt['filesize'] else None
        
        result['video_formats'][label] = {
            'size_mb': size_mb,  # Can be None
            'codec': best_fmt['vcodec'],
            'format_id': best_fmt['format_id'],
            'ext': best_fmt['ext'],
        }
```

---

## Bug #4 — Quality Key Mismatch Between Keyboard and `download_exec.py` (CRITICAL)

### Location
`bot/keyboards/inline/download.py` vs `bot/handlers/download_exec.py` — line 81–89

### Description
The keyboard emits `callback_data="quality_1440"` (no "p" suffix), but `download_exec.py` has a hardcoded `quality_map` that uses keys like `"1080"` (not `"1080p"` or `"1440"`):

```python
# ❌ Keyboard callback values
"quality_4k", "quality_1440", "quality_1080", "quality_720", ...

# ❌ format_handler.py extracts the key as:
quality_key = query.data.replace("quality_", "")
# Result: "4k", "1440", "1080", "720", "480", ...

# ❌ download_exec.py quality_map:
quality_map = {
    "4k": 2160,
    "1080": 1080,   # ← Matches "1080" ✅
    "720": 720,     # ← Matches "720" ✅
    "480": 480,     # ← Matches "480" ✅
    "360": 360,
    "240": 240
    # ← "1440" is MISSING! Will fall back to default 1080px
}
```

`"1440"` is not in the map at all, so it silently falls back to the default `1080`. This is a data-corruption bug in the download selection logic.

### Solution
Add `"1440"` to `quality_map` in `download_exec.py`:

```python
# ✅ FIXED
quality_map = {
    "4k": 2160,
    "1440": 1440,   # ← Added
    "1080": 1080,
    "720": 720,
    "480": 480,
    "360": 360,
    "240": 240,
}
```

---

## Bug #5 — `prepare_filename()` Returns Wrong Extension After Merging (HIGH)

### Location
`bot/handlers/download_exec.py` — lines 160–163

### Description
`yt_dlp.prepare_filename(info)` returns the **pre-merge** filename (e.g., `.webm` for the video-only stream), but after yt-dlp merges audio+video using ffmpeg, the actual file on disk might be `.mp4` or `.mkv`. The code then checks `os.path.exists(filename)` on the original extension path, which **doesn't exist**, causing a `FileNotFoundError` loop.

```python
# ❌ BEFORE
def run_ytdlp():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)  # Returns pre-merge name
```

### Solution
Use a wildcard glob to find the actual downloaded file by base name:

```python
# ✅ FIXED
import glob

def run_ytdlp():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_filename = ydl.prepare_filename(info)
        # Strip extension and search for any file with that base name
        base = os.path.splitext(raw_filename)[0]
        matches = glob.glob(f"{base}.*")
        if matches:
            # Return the largest file (the merged video)
            return max(matches, key=os.path.getsize)
        return raw_filename  # Fallback
```

---

## Bug #6 — Codec-Filtered Format String May Fail If Codec Unavailable (MEDIUM)

### Location
`bot/handlers/download_exec.py` — lines 91–98

### Description
When the user selects `h264` codec but the video only has `vp9` or `av01` streams, the format selector `bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]/best` will return `best` — which might be a resolution **higher** than requested. The `/best` fallback at the end is completely unconstrained.

### Solution
Always include a height constraint in the final fallback:

```python
# ✅ FIXED
if codec == "h264":
    ydl_opts["format"] = (
        f"bestvideo[height<={height}][vcodec*=avc]+bestaudio[ext=m4a]"
        f"/bestvideo[height<={height}][ext=mp4]+bestaudio"
        f"/best[height<={height}]"
    )
elif codec == "av1":
    ydl_opts["format"] = (
        f"bestvideo[height<={height}][vcodec^=av01]+bestaudio"
        f"/best[height<={height}]"
    )
elif codec == "vp9":
    ydl_opts["format"] = (
        f"bestvideo[height<={height}][vcodec^=vp09]+bestaudio"
        f"/bestvideo[height<={height}][vcodec^=vp9]+bestaudio"
        f"/best[height<={height}]"
    )
else:
    ydl_opts["format"] = (
        f"bestvideo[height<={height}]+bestaudio"
        f"/best[height<={height}]"
    )
```

---

## Bug #7 — `get_video_quality_keyboard` Size Display Can Crash on `None` (LOW)

### Location
`bot/keyboards/inline/download.py` — lines 40–68

### Description
After fixing Bug #3, `size_mb` can be `None`. The current keyboard formatting uses `f"{size:.1f} MB"` which will raise a `TypeError: unsupported format character` when `size` is `None`.

### Solution
Add a `None` guard in the keyboard builder:

```python
# ✅ FIXED (example for 4k)
if "4k" in format_info:
    size = format_info["4k"].get("size_mb")
    size_str = f"{size:.1f} MB" if size else "حجم: نامشخص"
    buttons.append([InlineKeyboardButton(
        text=f"🔵 4K (2160p) • {size_str}",
        callback_data="quality_4k"
    )])
```

---

## Summary Table

| # | Bug | Severity | File | Status |
|---|-----|----------|------|--------|
| 1 | No bot-detection bypass in yt-dlp opts | 🔴 CRITICAL | `utils/format_sizes.py` | Pending Fix |
| 2 | `get_event_loop()` deprecation | 🟡 MEDIUM | `utils/format_sizes.py` | Pending Fix |
| 3 | `filesize` gate skips valid formats → empty quality list | 🔴 CRITICAL | `utils/format_sizes.py` | Pending Fix |
| 4 | `"1440"` missing from `quality_map` | 🔴 CRITICAL | `download_exec.py` | Pending Fix |
| 5 | `prepare_filename()` returns pre-merge extension | 🔴 HIGH | `download_exec.py` | Pending Fix |
| 6 | Codec format string fallback not height-constrained | 🟡 MEDIUM | `download_exec.py` | Pending Fix |
| 7 | `None` size crashes keyboard string formatting | 🟢 LOW | `download.py` keyboards | Pending Fix |
