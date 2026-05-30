# ⚡ چک‌لیست سریع اشکال‌زدایی — خلاصه اجرایی

> **برای متخصصین و ایجنت‌های AI**: این خلاصه برای decision-making سریع است.  
> **فایل کامل**: `PROJECT_AUDIT_ANALYSIS.md`

---

## 📌 12 ایراد شناسایی‌شده (اولویت‌بندی شده)

### 🔴 **بحرانی** (Fix این‌ها ابتدا)

#### 1️⃣ عدم تطابق مستندات (ROADMAP ↔️ README)
```
ROADMAP.md: Phase 1 ❌ نکمل
README.md:  Phase 1 ✅ 100% complete
════════════════════════════════════════════
❌ کدام درست است؟
✅ حل: یک فایل "PROJECT_ACTUAL_STATUS.md" بسازید
```

#### 2️⃣ Syntax Errors در "We want build this.md"
```python
❌ initit__(self):         # باید __init__(self):
❌ Pfilele__).parent       # باید Path(__file__).parent
❌ tablename = "users"     # باید __tablename__ = "users"

✅ حل: تمام syntax errors را اصلاح کنید (کد block به block)
```

#### 3️⃣ ساختار پروژه نامشخص
```
❓ کدام فایل‌ها واقعاً پیاده‌سازی شده‌اند؟
❓ کدام دایرکتوری‌ها توخالی هستند؟
❓ کدام فایل‌های Python ناقص‌اند؟

✅ حل: یک "STRUCTURE_VERIFICATION.md" بسازید که:
   ✅ موجود (complete)
   🔄 در دست کار (partial)
   ❌ ناقص (needs work)
   ⚪ پیش‌نویس (placeholder)
```

---

### 🟡 **متوسط** (Fix بعد)

#### 4️⃣ ModuleRegistry — auto-discovery ناقص
```python
❌ Priority-based selection نیست
❌ Fallback logic نیست
❌ مدول بارگذاری failures handled نمی‌شود

✅ حل: اضافه کنید
   - PRIORITY attribute برای هر module
   - Graceful fallback برای missing modules
```

#### 5️⃣ CachedFile Model — Unique Constraint فقدان
```python
❌ تنها Index داده شده (composite index)
❌ هیچ UNIQUE constraint نیست
❌ Duplicate caches ممکن هستند

✅ حل: اضافه کنید
   UniqueConstraint('url_hash', 'format_id', 'codec')
```

#### 6️⃣ Progress Throttling — Logic ناقص
```python
❌ مشخص نیست چطور 3-second throttling کنیم
❌ Race condition ممکن است (بدون lock)

✅ حل: استفاده کنید
   - asyncio.Lock برای prevent concurrent updates
   - time.time() check برای throttle interval
```

#### 7️⃣ FSM States — Transitions غیرواضح
```python
❌ اگر Audio انتخاب کردند، CODEC و SEND_AS skip شود؟
❌ کدام state‌ها conditional هستند؟
❌ Back button flow مشخص نیست

✅ حل: درست کنید
   - وضوح دهید کدام state‌ها conditional
   - State diagram رسم کنید
   - Video/Audio branches جدا کنید
```

#### 8️⃣ Referral System — Reward Logic مبهم
```python
❌ اگر 5 دعوت: 50 coins؟ یا 10+10+10+10+10?
❌ کی rewards apply شود؟ بلافاصله یا batch?
❌ Milestone tracking mechanism نیست

✅ حل:
   - Milestone tracker اضافه کنید (only NEW milestones reward)
   - واضح کنید: 1=10, 5=50, 10=100, etc.
   - Batch processing یا real-time؟
```

#### 9️⃣ Payment Gateway — بدون Fallback
```python
❌ اگر CryptoBot credential نیست?
❌ اگر gateway call fail شود?
❌ بدون fallback strategy

✅ حل:
   - get_available_gateways() برای priority order
   - try/except با fallback logic
   - Unified webhook handler برای همه gateways
```

#### 🔟 Alembic Migrations — فایل‌های خالی
```python
❌ migrations/versions/ خالی است
❌ اگر models updated، migrations باید generate شود

✅ حل:
   - Generate migrations: alembic revision --autogenerate -m "..."
   - Verify script بسازید برای check
```

---

### 🟢 **کم** (اختیاری)

#### 1️⃣1️⃣ Localization — فقط structure
```
locales/fa/messages.json  ← Empty?
locales/en/messages.json  ← Empty?
...

✅ حل: واقعی messages اضافه کنید (تاب دوم)
```

#### 1️⃣2️⃣ Test Framework — inconsistent
```
test_*.py files کثیر هستند، اما نه:
- pytest.ini
- conftest.py
- Coverage reports

✅ حل: tests/ directory سازمان‌دهی کنید (تاب سوم)
```

---

## 📊 خلاصه سریع

| # | ایراد | شدت | حل |
|---|-------|------|-----|
| 1 | مستندات تناقض | 🔴 | `PROJECT_ACTUAL_STATUS.md` |
| 2 | Syntax errors | 🔴 | بحرف بحرف fix کنید |
| 3 | ساختار مبهم | 🔴 | `STRUCTURE_VERIFICATION.md` |
| 4 | ModuleRegistry | 🟡 | Priority + fallback |
| 5 | CachedFile | 🟡 | Unique constraint |
| 6 | Progress | 🟡 | Lock + throttle |
| 7 | FSM states | 🟡 | State diagram |
| 8 | Referral | 🟡 | Milestone logic |
| 9 | Payment | 🟡 | Fallback gateway |
| 10 | Migrations | 🟡 | Generate + verify |
| 11 | Locales | 🟢 | Messages اضافه کنید |
| 12 | Tests | 🟢 | pytest.ini |

---

## 🚀 ترجیح ترتیب اجرا

### **مرحله 1: توثیق (روز 1)**
```
1. ✅ Create PROJECT_ACTUAL_STATUS.md
   - کدام فایل‌ها واقعاً پیاده‌سازی شده‌اند؟
   - نسخه‌ی last commit هر مدول؟

2. ✅ Fix syntax errors in "We want build this.md"
   - Copy/paste صحیح می‌شود

3. ✅ Create STRUCTURE_VERIFICATION.md
   - ✅ Complete
   - 🔄 Partial  
   - ❌ Missing
```

### **مرحله 2: اصلاحات اساسی (روز 2-3)**
```
1. 🔧 ModuleRegistry (priority + fallback)
2. 🔧 CachedFile (unique constraint)
3. 🔧 Payment gateway (fallback)
4. 🔧 Progress updater (lock + throttle)
```

### **مرحله 3: Enhancements (روز 4+)**
```
1. 📝 FSM state diagram
2. 📝 Referral logic clarification
3. 📝 Alembic migration generation
4. 📝 Localization messages
5. 🧪 Test framework organization
```

---

## 💡 نکات کلیدی برای تیم

### **برای Human Developers**:
✅ `PROJECT_AUDIT_ANALYSIS.md` را بخوانید برای **تمام جزئیات**  
✅ هر ایراد دارای **راه‌حل با کد** است  
✅ Copy/paste کنید و modify کنید  

### **برای AI Agents (Cursor/GPT)**:
✅ این checklist برای **task prioritization** است  
✅ `PROJECT_AUDIT_ANALYSIS.md` دارای **implementation-ready code** است  
✅ Syntax errors در ۳ فایل روشن است  

### **برای Managers**:
✅ 3 ایراد بحرانی وجود دارد (روز 1)  
✅ 7 ایراد متوسط (روز 2-4)  
✅ 2 ایراد کم (هفته دوم+)  
✅ Total effort: **1-2 هفته** (با تیم متخصص)

---

## 📄 فایل‌های مرتبط

```
📌 PROJECT_AUDIT_ANALYSIS.md    ← فایل کامل (34KB)
📌 QUICK_AUDIT_CHECKLIST.md     ← این فایل (خلاصه)
📌 ROADMAP.md                   ← نقشه‌راه
📌 README.md                    ← وضعیت ادعا شده
📌 We want build this.md        ← پرامپت (with errors)
```

---

**آخرین بروزرسانی**: 2026-05-28  
**نسخه**: 1.0  
✅ آماده برای پیاده‌سازی
