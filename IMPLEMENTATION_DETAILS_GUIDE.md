# 📖 راهنمای تفصیلی اجرای هر Item

> **این فایل**: Step-by-step instructions برای اجرای هر item در **PHASED_IMPLEMENTATION_ROADMAP.md**  
> **استفاده**: با PHASED_IMPLEMENTATION_ROADMAP.md همراه استفاده کنید

---

## 🎯 Navigation

**PHASE 1** (روز 1):
- [Item 1.1: ROADMAP.md](#phase-1-item-11-اصلاح-roadmapmd)
- [Item 1.2: README.md](#phase-1-item-12-اصلاح-readmemd)
- [Item 1.3: We want build this.md](#phase-1-item-13-اصلاح-we-want-build-thismd)

**PHASE 2** (روز 2-3):
- [Item 2.1: ModuleRegistry](#phase-2-item-21-اصلاح-moduleregistry)
- [Item 2.2: CachedFile](#phase-2-item-22-اصلاح-cachedfile-model)
- [Item 2.3: Progress](#phase-2-item-23-اصلاح-progress-updater)
- [Item 2.4: FSM](#phase-2-item-24-اصلاح-fsm-states)
- [Item 2.5: Referral](#phase-2-item-25-اصلاح-referral-system)
- [Item 2.6: Payment](#phase-2-item-26-اصلاح-payment-gateway)
- [Item 2.7: Migrations](#phase-2-item-27-اصلاح-alembic-migrations)

**PHASE 3** (روز 4+):
- [Item 3.1: Localization](#phase-3-item-31-اصلاح-localization)
- [Item 3.2: Tests](#phase-3-item-32-اصلاح-test-framework)

---

# PHASE 1: اصلاح مستندات

## PHASE 1 - Item 1.1: اصلاح ROADMAP.md

### 🎯 هدف
ROADMAP.md را تمیز کنید و وضعیت واقعی را document کنید.

### 📋 مراحل اجرا

#### مرحله 1: فایل را باز کنید
```bash
# Windows
notepad "d:\telgram bot md backup 2- Copy\ROADMAP.md"

# یا محدث‌ترین editor استفاده کنید
code "d:\telgram bot md backup 2- Copy\ROADMAP.md"
```

#### مرحله 2: تمام timestamps حذف کنید
```markdown
❌ قبل:
[5/20/2026 19:40] reza: # نقشه‌راه پیاده‌سازی
[5/20/2026 19:40] reza: - [ ] 1.1.1 تعریف مدل‌های اصلی

✅ بعد:
# نقشه‌راه پیاده‌سازی
- [ ] 1.1.1 تعریف مدل‌های اصلی
```

**نحوه انجام**: 
- Find/Replace استفاده کنید
- Pattern: `\[5/[0-9/]+ [0-9:]+\] \w+: `
- Replace: (خالی)

#### مرحله 3: وضعیت فاز را تعریف کنید
```markdown
# فاز 1 — MVP: یوتیوب دانلودر
**وضعیت**: 🔄 IN PROGRESS (نه ❌ تکمیل نشده)

## Progress Tracking
- Total Tasks: 48
- Completed: 12
- In Progress: 8
- Not Started: 28
- Estimated Completion: TBD

**Last Updated**: 2026-05-28
```

#### مرحله 4: Status table اضافه کنید
```markdown
## فاز‌های پروژه — خلاصه

| فاز | عنوان | Status | Progress | Deadline |
|-------|--------|--------|----------|----------|
| Phase 1 | MVP: YouTube Downloader | 🔄 In Progress | 25% | TBD |
| Phase 2 | Monetization & Features | 🔴 Blocked | 0% | TBD |
| Phase 3 | Multi-Platform | 🔴 Not Started | 0% | TBD |
```

#### مرحله 5: محتوا را organize کنید
```markdown
✅ کیفیات خوب برای نگاه داریم:
- فاز‌های واضح (1, 2, 3)
- Sub-tasks numbered
- Checklists با [ ]
- Status per task

❌ غلط‌های حذف شده:
- Timestamps
- Random notes
- Incomplete sentences
- Mixed languages
```

### ✅ Verification

```bash
# 1. Syntax check
grep -E "\[5/[0-9/]+" ROADMAP.md
# Output: (باید خالی باشد)

# 2. Structure check
grep "^#" ROADMAP.md
# Output: باید تمام headers را show کند

# 3. Formatting check
# Manually: باز کنید در editor
# ✓ Headers درست
# ✓ Lists برابر
# ✓ Tables align شده
# ✓ Code blocks valid
```

### 📝 Checklist اتمام

- [ ] تمام timestamps حذف شدند
- [ ] وضعیت فاز‌ها واضح است
- [ ] Status table اضافه شد
- [ ] Formatting consistent است
- [ ] File خوانایی ممتاز دارد
- [ ] با README.md ناسازگاری نیست (یا resolve شد)
- [ ] Git commit: "docs: Clean up ROADMAP.md - remove timestamps, add status tracking"

---

## PHASE 1 - Item 1.2: اصلاح README.md

### 🎯 هدف
README.md وضعیت واقعی را reflect کند (نه بزرگ‌نمایش‌شده).

### 📋 مراحل اجرا

#### مرحله 1: فایل را باز کنید
```bash
code "d:\telgram bot md backup 2- Copy\README.md"
```

#### مرحله 2: Claims اصلی را check کنید
```markdown
Current Claims:
✅ Phase 1 MVP ✅ 100% COMPLETE
✅ Phase 2: Monetization 🔄 85% IN PROGRESS
✅ Phase 3: Multi-Platform ✅ 100% COMPLETE

❓ Questions:
- کدام فایل‌ها واقعاً implement شده‌اند؟
- کدام فایل‌ها skeleton تنها هستند؟
- کدام handlers active هستند؟
- کدام tests passing هستند؟
```

#### مرحله 3: Actual Code Audit انجام دهید
```bash
# Python files موجود؟
find . -name "*.py" -type f | grep -E "(bot|modules|services|database)" | sort

# Module system working؟
python -c "from modules import registry; print(registry.get_all_modules())"

# Database models exist؟
find . -path "./database/models/*.py" -type f

# Web panel exist؟
ls -la web/

# Tests run؟
pytest --collect-only
```

#### مرحله 4: Status را accurate update کنید

```markdown
❌ غلط (بزرگ‌نمایش‌شده):
### Phase 1: MVP ✅ 100% COMPLETE
- ✅ YouTube downloader (yt-dlp with format parsing & quality selection)
- ✅ Large file uploads (Pyrogram: up to 4GB via MTProto)
...

✅ درست (honest):
### Phase 1: MVP 🔄 50% COMPLETE
- ✅ Architecture designed and documented
- ✅ Project structure created
- 🔄 YouTube downloader (in progress)
- ❌ Large file uploads (not yet implemented)
- ❌ Progress tracking (not yet implemented)
...

**Note**: See ROADMAP.md for detailed breakdown per task.
```

#### مرحله 5: Consistency check اضافه کنید
```markdown
## 🔄 Project Status

Last Updated: 2026-05-28
Truth Source: ROADMAP.md + Code Audit

For detailed breakdown:
- 📋 ROADMAP.md - Complete task list with status
- 📊 PHASED_IMPLEMENTATION_ROADMAP.md - Implementation plan
- 🔍 PROJECT_AUDIT_ANALYSIS.md - Issues and solutions
```

### ✅ Verification

```bash
# 1. Check claims vs. code
# README می‌گوید X complete
# Code audit کند: X really complete?

# 2. Consistency check
grep "100% COMPLETE\|85% IN PROGRESS\|100% COMPLETE" README.md
# Verify each claim manually

# 3. Cross-reference
# README.md ↔ ROADMAP.md ↔ Actual code
# باید match کنند
```

### 📝 Checklist اتمام

- [ ] تمام status claims verified شدند
- [ ] Honest descriptions نوشته‌شدند
- [ ] Actual code matches documentation
- [ ] ROADMAP.md reference اضافه شد
- [ ] Future work واضح است
- [ ] No misleading statements
- [ ] Git commit: "docs: Update README with accurate status based on code audit"

---

## PHASE 1 - Item 1.3: اصلاح "We want build this.md"

### 🎯 هدف
Syntax errors و formatting مشکلات را اصلاح کنید.

### 📋 مراحل اجرا

#### مرحله 1: فایل را باز کنید
```bash
code "d:\telgram bot md backup 2- Copy\We want build this.md"
```

#### مرحله 2: تمام timestamps حذف کنید
```bash
# PowerShell یا bash
# Find and replace: ^\[5/20/2026 [0-9:]+\] \w+: 
# Replace: (empty)

# Manual approach:
# Ctrl+H (Find Replace)
# Find: [5/20/2026 
# Replace: (کنسل کنید)
```

#### مرحله 3: Syntax Errors اصلاح کنید

**Error 1: `initit__` → `__init__`**
```python
# Line: ~343
❌ initit__(self):
✅ def __init__(self):
```

**Error 2: `Pfilele__` → `Path(__file__)`**
```python
# Line: ~348
❌ modules_path = Pfilele__).parent
✅ modules_path = Path(__file__).parent
```

**Error 3: `tablename` → `__tablename__`**
```python
# Line: ~400
❌ tablename = "users"
✅ __tablename__ = "users"
```

**Find and replace تمام SQLAlchemy models**:
```bash
# Find: ^    tablename = 
# Replace: ^    __tablename__ = 
```

#### مرحله 4: Code blocks صحیح کنید

```markdown
❌ غلط:
@dataclass
class MediaInfo:
    url: str
    ...

✅ درست:
```python
@dataclass
class MediaInfo:
    url: str
    ...
```
```

**Regex for fixing**:
```bash
# Find: ^python\n
# Replace: ```python\n

# Find: ^`\n
# Replace: ```\n
```

#### مرحله 5: Formatting normalize کنید

```bash
# 1. Indentation: Tabs → Spaces (4 spaces)
# 2. Line endings: Windows (CRLF) → Unix (LF)
# 3. Trailing spaces: Remove all
# 4. Empty lines: Max 2 consecutive
```

### ✅ Verification

```bash
# 1. Python syntax check برای code blocks
python -m py_compile <test_file>

# 2. Markdown validation
# Online: https://www.markdownlint.com/
# Or: npm install -g markdownlint-cli

# 3. Manual check
# - تمام code blocks valid Python؟
# - تمام markdown tables proper؟
# - تمام links working؟
```

### 📝 Checklist اتمام

- [ ] تمام timestamps حذف شدند
- [ ] `initit__` → `__init__` fixed
- [ ] `Pfilele__` → `Path(__file__)` fixed
- [ ] `tablename` → `__tablename__` fixed
- [ ] تمام code blocks proper Python
- [ ] Formatting consistent
- [ ] Markdown valid
- [ ] Git commit: "docs: Fix syntax errors in We want build this.md"

---

# PHASE 2: اصلاح منطق و معماری

## PHASE 2 - Item 2.1: اصلاح ModuleRegistry

### 🎯 هدف
Priority-based module selection و fallback logic implement کنید.

### 📋 مراحل اجرا

#### Step 1: `modules/base.py` update کنید
```python
# Add PRIORITY attribute
class BaseDownloader(ABC):
    NAME: str = ""
    ICON: str = ""
    SUPPORTED_DOMAINS: list[str] = []
    VERSION: str = "1.0.0"
    ENABLED: bool = True
    PRIORITY: int = 0  # ← NEW: higher = tried first
```

#### Step 2: `modules/__init__.py` update کنید
```python
# From PROJECT_AUDIT_ANALYSIS.md Issue #4
# Copy complete solution code

class ModuleRegistry:
    def __init__(self):
        self._modules: list[tuple[int, type[BaseDownloader]]] = []
        self._discover_modules()
    
    def _discover_modules(self):
        """Auto-discover modules from modules/ directory"""
        # ... implementation from audit report
    
    def get_handler(self, url: str) -> type[BaseDownloader] | None:
        """Get handler for URL, respecting priority"""
        for _, module in self._modules:
            if module.can_handle(url):
                return module
        return None
```

#### Step 3: YouTube module update کنید
```python
# modules/youtube/downloader.py
class YouTubeDownloader(BaseDownloader):
    NAME = "YouTube"
    ICON = "▶️"
    SUPPORTED_DOMAINS = ["youtube.com", "youtu.be", "youtube-nocookie.com"]
    VERSION = "1.0.0"
    ENABLED = True
    PRIORITY = 10  # High priority
```

#### Step 4: Test کنید
```bash
# python
from modules import registry

# Should auto-discover
modules = registry.get_all_modules()
print(f"Discovered {len(modules)} modules")

# Test priority
url = "https://www.youtube.com/watch?v=..."
handler = registry.get_handler(url)
print(f"Handler: {handler.NAME}")

# Test fallback (invalid URL)
handler = registry.get_handler("https://invalid.example.com")
print(f"Fallback: {handler}")  # Should be None, handled gracefully
```

### ✅ Verification
- [ ] PRIORITY attribute به BaseDownloader اضافه شد
- [ ] ModuleRegistry priority sorting implement شد
- [ ] Auto-discovery working
- [ ] Tests pass
- [ ] Git commit: "feat: Add priority-based module selection with fallback"

---

## PHASE 2 - Item 2.2: اصلاح CachedFile Model

### 🎯 هدف
Unique constraint اضافه کنید تا duplicate caches prevent شود.

### 📋 مراحل اجرا

#### Step 1: `database/models/cached_file.py` update کنید
```python
from sqlalchemy import UniqueConstraint

class CachedFile(Base):
    __tablename__ = "cached_files"
    
    # ... existing columns ...
    
    __table_args__ = (
        UniqueConstraint('url_hash', 'format_id', 'codec', 
                        name='uq_cached_files_lookup'),
        Index('ix_cached_files_platform', 'platform', 'video_id'),
        Index('ix_cached_files_telegram_id', 'telegram_file_id'),
    )
```

#### Step 2: Migration generate کنید
```bash
cd /path/to/project

# Generate migration
alembic revision --autogenerate -m "Add unique constraint to CachedFile"

# Check generated file
ls migrations/versions/

# The file should be something like:
# migrations/versions/001_add_unique_constraint_to_cached_file.py
```

#### Step 3: Migration test کنید
```bash
# Check migration
alembic current
# Output: (should show current version)

# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Verify table structure
psql -d dlbot_db -c "\d cached_files"
# Should show unique constraint
```

#### Step 4: Code test کنید
```python
# test_cached_file.py
from database.models.cached_file import CachedFile
from sqlalchemy.exc import IntegrityError

async def test_unique_constraint():
    session = AsyncSession(engine)
    
    # Create first record
    file1 = CachedFile(
        url_hash="hash1",
        format_id="fmt1", 
        codec="h264",
        telegram_file_id="file123"
    )
    session.add(file1)
    await session.commit()
    
    # Try to create duplicate (should fail)
    file2 = CachedFile(
        url_hash="hash1",
        format_id="fmt1",
        codec="h264",
        telegram_file_id="file456"
    )
    session.add(file2)
    
    try:
        await session.commit()
        assert False, "Should have raised IntegrityError"
    except IntegrityError:
        print("✓ Unique constraint working!")
```

### ✅ Verification
- [ ] CachedFile model updated with unique constraint
- [ ] Migration file generated
- [ ] Migration tested (upgrade/downgrade)
- [ ] Duplicate prevention confirmed
- [ ] Tests pass
- [ ] Git commit: "database: Add unique constraint to CachedFile model"

---

## PHASE 2 - Item 2.3: اصلاح Progress Updater

### 🎯 هدف
Progress message throttling با 3-second interval implement کنید.

### 📋 مراحل اجرا

#### Step 1: `utils/progress.py` check/update کنید
```python
def generate_progress_message(
    title: str,
    progress_percent: float,
    downloaded_mb: float,
    total_mb: float,
    speed_mbps: float,
    eta_seconds: int,
    queue_position: int = 0,
    phase: str = "download"
) -> str:
    """Generate beautifully formatted progress message"""
    # ... (copy from audit report)
```

#### Step 2: `services/download_service.py` میں ProgressUpdater class بسازید
```python
import time
import asyncio

class ProgressUpdater:
    def __init__(self, throttle_interval: int = 3):
        self._lock = asyncio.Lock()
        self._last_update = 0
        self._throttle_interval = throttle_interval
    
    async def update_progress(self, message, progress_data):
        """Update with throttling to prevent message flood"""
        async with self._lock:
            current_time = time.time()
            
            if current_time - self._last_update < self._throttle_interval:
                return  # Skip update
            
            try:
                new_text = generate_progress_message(**progress_data)
                await message.edit_text(
                    new_text,
                    parse_mode="HTML"
                )
                self._last_update = current_time
            except Exception as e:
                logger.warning(f"Progress update failed: {e}")
```

#### Step 3: Handler میں استفاده کنید
```python
# bot/handlers/download.py
async def download_handler(msg: Message, state: FSMContext):
    updater = ProgressUpdater(throttle_interval=3)
    progress_msg = await msg.answer("⏳ شروع...")
    
    # Simulate download
    for i in range(0, 101, 5):
        await updater.update_progress(
            progress_msg,
            {
                'title': 'Video Title',
                'progress_percent': i,
                'downloaded_mb': i * 2,
                'total_mb': 200,
                'speed_mbps': 5.2,
                'eta_seconds': max(0, (100-i) * 12),
            }
        )
        await asyncio.sleep(0.5)  # Simulate download
```

#### Step 4: Test کنید
```bash
# Test throttling behavior
pytest tests/test_progress_updater.py -v

# Expected:
# - 100 calls to update_progress
# - فقط ~34 calls go through (100 / 3 seconds)
# - Throttling working correctly
```

### ✅ Verification
- [ ] ProgressUpdater class implemented
- [ ] Throttling logic working (max 1 per 3s)
- [ ] asyncio.Lock preventing race conditions
- [ ] Tests pass
- [ ] Performance acceptable
- [ ] Git commit: "feat: Implement progress message throttling"

---

## PHASE 2 - Item 2.4: اصلاح FSM States

### 🎯 هدف
FSM state branches واضح کنید (Video vs Audio paths).

### 📋 مراحل اجرا

#### Step 1: `bot/states/download.py` update کنید
```python
from aiogram.fsm.state import State, StatesGroup

class DownloadStates(StatesGroup):
    WAITING_URL = State()
    SELECTING_FORMAT_TYPE = State()          # Video or Audio
    
    # Video-specific
    VIDEO_QUALITY_SELECTION = State()
    VIDEO_CODEC_SELECTION = State()
    
    # Audio-specific  
    AUDIO_FORMAT_SELECTION = State()
    
    # Common
    SELECTING_SUBTITLE = State()
    SELECTING_SEND_AS = State()              # Video only
    
    # Download
    DOWNLOADING = State()
    UPLOADING = State()
    COMPLETED = State()
```

#### Step 2: State diagram بسازید
```markdown
# State Machine Diagram

WAITING_URL
    ↓
SELECTING_FORMAT_TYPE
    ├─ [🎬 Video] → VIDEO_QUALITY_SELECTION
    │                      ↓
    │              VIDEO_CODEC_SELECTION
    │                      ↓
    │              SELECTING_SUBTITLE (optional)
    │                      ↓
    │              SELECTING_SEND_AS
    │                      ↓
    │              [DOWNLOADING] ────┐
    │                                 ↓
    │                          UPLOADING
    │                                 ↓
    │                          COMPLETED
    │
    └─ [🎵 Audio] → AUDIO_FORMAT_SELECTION
                            ↓
                    SELECTING_SUBTITLE (optional)
                            ↓
                    [DOWNLOADING] ────┐
                                      ↓
                              UPLOADING
                                      ↓
                              COMPLETED
```

#### Step 3: Handlers update کنید
```python
# bot/handlers/download.py

@router.message(DownloadStates.SELECTING_FORMAT_TYPE)
async def process_format_type(msg: Message, state: FSMContext):
    if msg.text == "🎬 ویدیو":
        await state.set_state(DownloadStates.VIDEO_QUALITY_SELECTION)
        await show_video_qualities(msg, state)
    elif msg.text == "🎵 صدا":
        await state.set_state(DownloadStates.AUDIO_FORMAT_SELECTION)
        await show_audio_formats(msg, state)

@router.message(DownloadStates.VIDEO_QUALITY_SELECTION)
async def process_video_quality(msg: Message, state: FSMContext):
    # Save quality
    await state.update_data(quality=msg.text)
    # Move to codec selection
    await state.set_state(DownloadStates.VIDEO_CODEC_SELECTION)
    await show_codec_selection(msg)

@router.message(DownloadStates.AUDIO_FORMAT_SELECTION)
async def process_audio_format(msg: Message, state: FSMContext):
    # Save format
    await state.update_data(audio_format=msg.text)
    # Skip codec, go to subtitle
    await state.set_state(DownloadStates.SELECTING_SUBTITLE)
    await show_subtitle_options(msg)
```

#### Step 4: Test کنید
```bash
pytest tests/test_fsm_states.py -v

# Test scenarios:
# 1. Video path: URL → Format → Quality → Codec → Subtitle → SendAs → Download
# 2. Audio path: URL → Format → Format Selection → Subtitle → Download
# 3. Back button handling
# 4. State transitions validation
```

### ✅ Verification
- [ ] States properly branched (video vs audio)
- [ ] Transitions clear and documented
- [ ] State diagram created
- [ ] Handlers implement transitions
- [ ] Tests pass for all paths
- [ ] Git commit: "feat: Implement video/audio branching in FSM states"

---

## PHASE 2 - Item 2.5: اصلاح Referral System

### 🎯 هدف
Referral rewards logic واضح و implement کنید.

### 📋 مراحل اجرا

#### Step 1: `services/referral_service.py` update کنید
```python
class ReferralService:
    MILESTONE_REWARDS = {
        1: {'coins': 10, 'badge': None},
        5: {'coins': 50, 'badge': 'دوستیابی 🌟'},
        10: {'coins': 100, 'badge': None},
        20: {'plan': 'silver', 'plan_days': 30},
        50: {'plan': 'gold', 'plan_days': 30},
    }
    
    async def process_referral(self, referrer_id: int, referred_id: int):
        """From audit report - copy complete implementation"""
        # ... (see PROJECT_AUDIT_ANALYSIS.md for full code)
```

#### Step 2: Database schema update
```python
# database/models/user.py - add milestone tracking
class User(Base):
    # ... existing fields ...
    referral_milestone: int = Column(Integer, default=0)  # Last milestone reached
    referral_badge: str = Column(String(50), nullable=True)  # Current badge
```

#### Step 3: Migration
```bash
alembic revision --autogenerate -m "Add referral milestone tracking"
alembic upgrade head
```

#### Step 4: Test کنید
```python
async def test_referral_rewards():
    # Scenario: referrer invites 5 people
    referrer_id = 123
    
    for i in range(1, 6):
        referred_id = 1000 + i
        rewards = await referral_service.process_referral(referrer_id, referred_id)
        print(f"Invite #{i}: {rewards}")
    
    # Expected:
    # Invite #1: [(1, {'coins': 10})]
    # Invite #2: []
    # Invite #3: []
    # Invite #4: []
    # Invite #5: [(5, {'coins': 50, 'badge': '...'})]
    
    # Total coins: 10 + 50 = 60
    user = await get_user(referrer_id)
    assert user.coins == 60
    assert user.referral_badge == 'دوستیابی 🌟'
```

### ✅ Verification
- [ ] Milestone tracking implemented
- [ ] Rewards only for NEW milestones
- [ ] Coin calculation correct
- [ ] Plan upgrades at correct milestones
- [ ] Tests pass
- [ ] Git commit: "feat: Implement milestone-based referral rewards"

---

## PHASE 2 - Item 2.6: اصلاح Payment Gateway

### 🎯 هدف
Payment fallback logic implement کنید.

### 📋 مراحل اجرا

#### Step 1: `services/payment_service.py` update
```python
class PaymentService:
    GATEWAY_PRIORITY = [
        PaymentGateway.CRYPTO_BOT,
        PaymentGateway.NOW_PAYMENTS,
        PaymentGateway.ZARINPAL,
    ]
    
    def get_available_gateways(self) -> list[PaymentGateway]:
        """Get available gateways in priority order"""
        return [
            gw for gw in self.GATEWAY_PRIORITY
            if self.enabled_gateways.get(gw, False)
        ]
    
    async def create_invoice(
        self,
        user_id: int,
        plan_type: UserPlanType,
        gateway: Optional[PaymentGateway] = None,
        currency: str = "USDT"
    ) -> tuple[str, PaymentGateway]:
        """Create invoice with fallback"""
        # From audit report - copy complete implementation
```

#### Step 2: Webhook handlers unify
```python
@router.post("/webhook/payment")
async def payment_webhook(request: Request):
    gateway = request.query_params.get("gateway")
    data = await request.json()
    
    result = await payment_service.handle_webhook(data, gateway)
    return {"status": "ok" if result else "error"}
```

#### Step 3: Test fallback
```python
async def test_payment_fallback():
    # Scenario: CryptoBot fails, should try NOWPayments
    
    # Mock CryptoBot to fail
    with patch('aiocryptopay.create_invoice', side_effect=Exception("Network error")):
        # Call create_invoice without specific gateway
        url, gateway_used = await payment_service.create_invoice(
            user_id=123,
            plan_type=UserPlanType.SILVER,
            # No gateway specified - will auto-select
        )
        
        # Should have used fallback
        assert gateway_used in [PaymentGateway.NOW_PAYMENTS, PaymentGateway.ZARINPAL]
```

### ✅ Verification
- [ ] get_available_gateways() working
- [ ] Fallback logic implemented
- [ ] Unified webhook handler
- [ ] Tests pass for fallback scenarios
- [ ] Git commit: "feat: Add payment gateway fallback strategy"

---

## PHASE 2 - Item 2.7: اصلاح Alembic Migrations

### 🎯 هدف
Initial migration generate کنید models سے.

### 📋 مراحل اجرا

#### Step 1: Alembic setup verify کریں
```bash
# Check if alembic initialized
ls -la migrations/env.py
ls -la migrations/alembic.ini

# If not, initialize:
# alembic init migrations
```

#### Step 2: Initial migration generate
```bash
# Generate migration from current models
alembic revision --autogenerate -m "Initial schema with all models"

# Check generated file
ls -la migrations/versions/
# Should show something like: 001_initial_schema_with_all_models.py
```

#### Step 3: Migration verify کریں
```bash
# Open the generated migration file
cat migrations/versions/001_initial_schema_with_all_models.py

# Should contain:
# - User table
# - CachedFile table (with unique constraint)
# - Plan table
# - Subscription table
# - Referral table
# - CoinTransaction table
# - Payment table
# - Channel table
```

#### Step 4: Test upgrade/downgrade
```bash
# Test upgrade
alembic upgrade head

# Verify schema
psql -d dlbot_db -c "\dt"
# Should list all tables

# Test downgrade
alembic downgrade -1

# Verify tables gone
psql -d dlbot_db -c "\dt"
# Should be empty or fewer tables

# Upgrade again
alembic upgrade head
```

### ✅ Verification
- [ ] Initial migration generated
- [ ] All models included
- [ ] Upgrade/downgrade working
- [ ] Schema verified in database
- [ ] Tests pass
- [ ] Git commit: "database: Generate initial schema migration"

---

# PHASE 3: تکمیل و Polish

## PHASE 3 - Item 3.1: اصلاح Localization

### 🎯 هدف
تمام locales JSON files populate کنید.

### 📋 مراحل اجرا

#### Step 1: Persian (فارسی) messages populate
```json
// locales/fa/messages.json
{
  "welcome": "خوش آمدید به DLBot 🤖",
  "language_select": "لطفاً زبان خود را انتخاب کنید:",
  "download": {
    "url_prompt": "لطفاً لینک ویدیو را ارسال کنید:",
    "format_select": "نوع فایل را انتخاب کنید:",
    "quality_select": "کیفیت را انتخاب کنید:",
    "progress_download": "⬇️ در حال دانلود...",
    "progress_upload": "⬆️ در حال ارسال به تلگرام...",
    "complete": "✅ دانلود تکمیل شد!",
    "error": "❌ خطای دانلود: {error}"
  },
  "referral": {
    "invite_link": "لینک دعوت‌شما: {link}",
    "referral_count": "تعداد دعوت‌شدگان: {count}",
    "coins_earned": "سکه‌های کسب‌شده: {coins}"
  }
}
```

#### Step 2: English messages
```json
// locales/en/messages.json
{
  "welcome": "Welcome to DLBot 🤖",
  "language_select": "Please select your language:",
  "download": {
    "url_prompt": "Please send the video link:",
    "format_select": "Select file type:",
    "quality_select": "Select quality:",
    "progress_download": "⬇️ Downloading...",
    "progress_upload": "⬆️ Uploading to Telegram...",
    "complete": "✅ Download complete!",
    "error": "❌ Download error: {error}"
  },
  "referral": {
    "invite_link": "Your invite link: {link}",
    "referral_count": "Referrals: {count}",
    "coins_earned": "Coins earned: {coins}"
  }
}
```

#### Step 3: Other languages (Arabic, Russian, Chinese)
```json
// Similar structure for locales/ar/, locales/ru/, locales/zh/
```

#### Step 4: Middleware test
```python
from locales.loader import I18nManager

i18n = I18nManager()

# Test Persian
msg_fa = i18n.translate("download.complete", "fa")
assert msg_fa == "✅ دانلود تکمیل شد!"

# Test English with interpolation
msg_en = i18n.translate(
    "referral.coins_earned",
    "en",
    coins=100
)
assert msg_en == "Coins earned: 100"
```

### ✅ Verification
- [ ] All JSON files populated
- [ ] All UI strings covered
- [ ] Interpolation working
- [ ] Middleware loading correctly
- [ ] Tests pass
- [ ] Git commit: "i18n: Complete localization messages for all languages"

---

## PHASE 3 - Item 3.2: اصلاح Test Framework

### 🎯 هدف
Test framework سازمان‌دهی اور pytest setup کنید.

### 📋 مراحل اجرا

#### Step 1: Directory structure بسازید
```bash
mkdir -p tests/test_unit
mkdir -p tests/test_integration
mkdir -p tests/test_e2e

# Move existing tests
mv test_*.py tests/test_e2e/
cd tests

# Create __init__.py files
touch __init__.py
touch test_unit/__init__.py
touch test_integration/__init__.py
touch test_e2e/__init__.py
```

#### Step 2: pytest.ini بسازید
```ini
# tests/pytest.ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html:coverage_html
    --cov-report=term-missing
    --cov-fail-under=70

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

#### Step 3: conftest.py بسازید
```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    """Test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

#### Step 4: Test cases organize
```bash
# tests/test_unit/test_models.py
# tests/test_unit/test_services.py
# tests/test_unit/test_utils.py

# tests/test_integration/test_download_flow.py
# tests/test_integration/test_referral_system.py

# tests/test_e2e/test_complete_workflow.py
```

#### Step 5: Run tests
```bash
# Run all tests
pytest

# Run specific category
pytest -m unit
pytest -m integration
pytest -m e2e

# With coverage
pytest --cov

# Generate HTML report
pytest --cov --cov-report=html
# Open coverage_html/index.html
```

### ✅ Verification
- [ ] tests/ directory structured
- [ ] pytest.ini configured
- [ ] conftest.py with fixtures
- [ ] Tests organized (unit/integration/e2e)
- [ ] Coverage reports generating
- [ ] CI/CD ready
- [ ] Git commit: "test: Reorganize test framework with pytest"

---

## 🎉 Completion!

تمام items تکمیل ہو گئے۔ اب:

1. ✅ تمام tests pass کریں
2. ✅ Code review کریں
3. ✅ Documentation update کریں
4. ✅ Deployment کے لیے تیار کریں

---

**Last Updated**: 2026-05-28  
**Status**: ✅ Ready for Implementation

