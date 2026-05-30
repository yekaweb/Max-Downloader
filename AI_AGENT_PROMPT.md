# 🤖 پرامپت برای هوش مصنوعی: پاک‌سازی و اصلاح پروژه DLBot

> **این پرامپت**: دستورالعملِ مفصل برای AI agent (Cursor، Claude، GPT)  
> **هدف**: خودکار اصلاح 12 ایراد شناسایی‌شده  
> **اصول**: Sequential NOT Parallel | هر فایل یکی‌یکی | تصدیق قبل از رفتن به بعدی

---

## 🎯 درک کامل از وضعیت

### فایل‌های راهنمایی (Reference Files)

ما **6 فایل راهنمایی** برای تو تهیه کرده‌ایم:

| فایل | مقصد | چه زمانی استفاده کنی |
|------|------|---------------------|
| **PROJECT_AUDIT_ANALYSIS.md** | تحلیل دقیق هر ایراد | وقتی ایراد را بخواهی درک کنی |
| **PHASED_IMPLEMENTATION_ROADMAP.md** | نقشه‌راه 3-فاز | برای ترتیب کار و فهم ساختار |
| **IMPLEMENTATION_DETAILS_GUIDE.md** | Step-by-step هر item | برای اجرای دقیق هر کار |
| **QUICK_AUDIT_CHECKLIST.md** | خلاصه سریع | برای overview سریع |
| **HOW_TO_USE_AUDIT_REPORTS.md** | نحوه استفاده | برای workflow |
| **AUDIT_SUMMARY.txt** | خلاصه‌ی شامل | برای status check |

### فایل‌های پروژه اصلی (Target Files)

تو باید **اینها** را اصلاح کنی:

| فایل | وضعیت | اولویت | وابستگی |
|------|--------|---------|----------|
| **ROADMAP.md** | ❌ نیاز اصلاح | 🔴 CRITICAL | None |
| **README.md** | ❌ نیاز اصلاح | 🔴 CRITICAL | ROADMAP done |
| **We want build this.md** | ❌ Syntax errors | 🔴 CRITICAL | README done |
| **modules/__init__.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **database/models/cached_file.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **services/download_service.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **bot/states/download.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **services/referral_service.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **services/payment_service.py** | ⚠️ ناقص | 🟡 MEDIUM | Phase 1 done |
| **migrations/versions/** | ❌ خالی | 🟡 MEDIUM | Phase 1 done |
| **locales/*/messages.json** | ❌ خالی | 🟢 LOW | Phase 2 done |
| **tests/** | ⚠️ Scattered | 🟢 LOW | Phase 2 done |

---

## 📋 سیستم اجرا: SEQUENTIAL NOT PARALLEL

### اصول مهم:

```
🚫 NEVER do this:
  - شروع کردن Item 2 قبل از Item 1 تمام شود
  - کار روی 2 فایل in PHASE 1 همزمان
  - رفتن به PHASE 2 قبل از PHASE 1 verification

✅ ALWAYS do this:
  - یک item کامل انجام دهید
  - تست کنید
  - Verify کنید
  - سپس رفتن به بعدی

⚠️ Exception: Within PHASE 2 می‌توانید parallel:
  - Item 2.1 + 2.2 توسط developer A
  - Item 2.3 + 2.4 توسط developer B
  - Item 2.5 + 2.6 + 2.7 توسط developer C
  
  اما PHASE 1 باید sequential باشد!
```

---

## 🚀 PHASE 1: اصلاح مستندات (روز 1)

### ⏱️ زمان: 2-3 ساعت
### 🎖️ اولویت: 🔴 **بحرانی**
### 🔗 Parallel: **نه، sequential**

---

### STEP 1.1: اصلاح ROADMAP.md

#### مقدمه:
```
فایل: ROADMAP.md
وضعیت: ❌ Broken
مشکل: Timestamps در متن + وضعیت غلط
هدف: تمیز و واضح
```

#### دستورات:
```
1. فایل ROADMAP.md را باز کن
   Location: d:\telgram bot md backup 2- Copy\ROADMAP.md

2. Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 1 - Item 1.1
   (تمام مراحل دقیق آنجا نوشته شده)

3. کار:
   ✓ تمام timestamps حذف کنید ([5/20/2026 ...])
   ✓ وضعیت فاز‌ها update کنید
   ✓ Status table اضافه کنید
   ✓ Formatting normalize کنید

4. Verify:
   - [ ] تمام timestamps gone
   - [ ] Status واضح
   - [ ] Formatting consistent
   - [ ] File excellent readability

5. Git:
   git commit -m "docs: Clean up ROADMAP.md - remove timestamps, add status tracking"

6. Report:
   "✅ PHASE 1 - Item 1.1 COMPLETED"
```

#### علامت‌گذاری:
```
قبل شروع:  [ ] ROADMAP.md
در حال انجام: [🔄] ROADMAP.md
تکمیل شد:  [✅] ROADMAP.md
```

---

### STEP 1.2: اصلاح README.md

#### مقدمه:
```
فایل: README.md
وضعیت: ❌ Broken (claims 100% complete)
مشکل: Status claims بزرگ‌نمایش‌شده
هدف: Honest و accurate
```

#### دستورات:
```
1. فایل README.md را باز کن
   Location: d:\telgram bot md backup 2- Copy\README.md

2. Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 1 - Item 1.2

3. کار:
   ✓ تمام status claims verify کنید
   ✓ ROADMAP.md consistency check کنید
   ✓ Actual code audit انجام دهید
   ✓ Honest descriptions بنویسید
   ✓ Future work واضح کنید

4. Verify:
   - [ ] Claims verified
   - [ ] Honest descriptions
   - [ ] Consistent with ROADMAP
   - [ ] No misleading statements

5. Git:
   git commit -m "docs: Update README with accurate status based on code audit"

6. Report:
   "✅ PHASE 1 - Item 1.2 COMPLETED"
```

#### علامت‌گذاری:
```
قبل شروع:  [ ] README.md
در حال انجام: [🔄] README.md
تکمیل شد:  [✅] README.md
```

---

### STEP 1.3: اصلاح "We want build this.md"

#### مقدمه:
```
فایل: We want build this.md
وضعیت: ❌ Broken (multiple syntax errors)
مشکل: initit__, Pfilele__, tablename غلط
هدف: Valid Python + Clean markdown
```

#### دستورات:
```
1. فایل را باز کن
   Location: d:\telgram bot md backup 2- Copy\We want build this.md

2. Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 1 - Item 1.3

3. کار (step-by-step):
   Step A: تمام timestamps حذف کنید
   Step B: Syntax Error 1 fix: initit__ → __init__
   Step C: Syntax Error 2 fix: Pfilele__ → Path(__file__)
   Step D: Syntax Error 3 fix: tablename → __tablename__
   Step E: تمام code blocks صحیح کنید
   Step F: Formatting normalize کنید

4. Verify:
   - [ ] No timestamps
   - [ ] No syntax errors
   - [ ] All code blocks valid
   - [ ] Markdown valid
   - [ ] Excellent formatting

5. Git:
   git commit -m "docs: Fix syntax errors in We want build this.md"

6. Report:
   "✅ PHASE 1 - Item 1.3 COMPLETED"
```

#### علامت‌گذاری:
```
قبل شروع:  [ ] We want build this.md
در حال انجام: [🔄] We want build this.md
تکمیل شد:  [✅] We want build this.md
```

---

## ✅ PHASE 1 Completion Check

```
❓ Is PHASE 1 completely done?

✓ ROADMAP.md:         [✅]
✓ README.md:          [✅]
✓ We want build this: [✅]

If all are [✅], then:
  1. تمام tests pass می‌کنند
  2. کوئی conflicts نیست
  3. مستندات sync شدند
  
THEN: آماده برای PHASE 2 ✅
ELSE: Back to failed item
```

---

## 🎯 PHASE 2: اصلاح منطق و معماری (روز 2-3)

### ⏱️ زمان: 4-6 ساعت
### 🎖️ اولویت: 🟡 **متوسط**
### 🔗 Parallel: ✅ **می‌توانید parallel** (هر 2-3 item)

### نکته مهم:
```
❌ NEVER شروع PHASE 2 تا PHASE 1 completely done نشود!

✅ کن:
   - Verify all PHASE 1 items
   - Run all tests
   - Check no conflicts
   - THEN شروع PHASE 2
```

---

### STEP 2.1-2.7: Items مستقل

#### ساختار:

```
هر item در PHASE 2:
├─ Reference فایل خاص: IMPLEMENTATION_DETAILS_GUIDE.md
├─ Reference roadmap: PHASED_IMPLEMENTATION_ROADMAP.md
├─ Code changes: کپی‌و‌پیست آماده
├─ Tests: تفصیلی شده
├─ Git commit: پیشنهاد شده
└─ Report: Status clear
```

#### 7 Items (می‌توانند parallel):

```
Item 2.1: ModuleRegistry
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.1
  └─ Files: modules/__init__.py, modules/base.py
  └─ Effort: 1-2 hours

Item 2.2: CachedFile Model
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.2
  └─ Files: database/models/cached_file.py, migrations/
  └─ Effort: 1-2 hours

Item 2.3: Progress Updater
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.3
  └─ Files: utils/progress.py, services/download_service.py
  └─ Effort: 1-2 hours

Item 2.4: FSM States
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.4
  └─ Files: bot/states/download.py, bot/handlers/download.py
  └─ Effort: 1-2 hours

Item 2.5: Referral System
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.5
  └─ Files: services/referral_service.py, database/models/user.py
  └─ Effort: 1-2 hours

Item 2.6: Payment Gateway
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.6
  └─ Files: services/payment_service.py, bot/handlers/plans.py
  └─ Effort: 1-2 hours

Item 2.7: Alembic Migrations
  └─ Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item 2.7
  └─ Files: migrations/, alembic.ini
  └─ Effort: 1 hour
```

#### دستورات برای هر item:

```
برای هر ITEM X.X:

1. فایل Reference باز کن:
   IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 2 - Item X.X

2. مراحل را follow کن:
   ✓ Step 1
   ✓ Step 2
   ✓ ...
   ✓ Final step

3. Verify کن:
   ✓ تمام checkboxes completed
   ✓ Tests passing
   ✓ No conflicts

4. Git commit:
   git commit -m "..."

5. Report:
   "✅ PHASE 2 - Item X.X COMPLETED"
```

#### علامت‌گذاری:

```
Item 2.1: [ ] Not Started  → [🔄] In Progress  → [✅] Completed
Item 2.2: [ ] Not Started  → [🔄] In Progress  → [✅] Completed
...
Item 2.7: [ ] Not Started  → [🔄] In Progress  → [✅] Completed
```

---

## ✅ PHASE 2 Completion Check

```
❓ All 7 items done?

Item 2.1: [✅]
Item 2.2: [✅]
Item 2.3: [✅]
Item 2.4: [✅]
Item 2.5: [✅]
Item 2.6: [✅]
Item 2.7: [✅]

If all done:
  1. تمام tests pass
  2. هیچ conflicts
  3. Code review ok
  
THEN: آماده برای PHASE 3 ✅
```

---

## 🎯 PHASE 3: تکمیل و Polish (روز 4+)

### ⏱️ زمان: 2-3 ساعت
### 🎖️ اولویت: 🟢 **کم**
### 🔗 Parallel: ✅ **می‌توانید parallel**

---

### STEP 3.1: Localization

```
فایل‌ها: locales/*/messages.json
Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 3 - Item 3.1
Effort: 1-2 hours

دستورات:
1. Reference میں تمام steps follow کنید
2. تمام languages populate کنید
3. Tests verify کنید
4. Git commit
5. Report status
```

---

### STEP 3.2: Test Framework

```
فایل‌ها: tests/, pytest.ini
Reference: IMPLEMENTATION_DETAILS_GUIDE.md → PHASE 3 - Item 3.2
Effort: 1 hour

دستورات:
1. Reference میں تمام steps follow کنید
2. tests/ directory organize کنید
3. pytest.ini اور conftest.py بسازید
4. Tests verify کنید
5. Git commit
6. Report status
```

---

## ✅ FINAL Completion Check

```
❓ All 12 items done?

PHASE 1:
  ✓ Item 1.1: [✅]
  ✓ Item 1.2: [✅]
  ✓ Item 1.3: [✅]

PHASE 2:
  ✓ Item 2.1: [✅]
  ✓ Item 2.2: [✅]
  ✓ Item 2.3: [✅]
  ✓ Item 2.4: [✅]
  ✓ Item 2.5: [✅]
  ✓ Item 2.6: [✅]
  ✓ Item 2.7: [✅]

PHASE 3:
  ✓ Item 3.1: [✅]
  ✓ Item 3.2: [✅]

If all 12 are [✅]:
  ✅ PROJECT CLEANUP COMPLETE
  ✅ ALL ISSUES FIXED
  ✅ READY FOR DEPLOYMENT
```

---

## 📞 Quick Reference

```
❓ کہاں سے شروع کروں؟
→ PHASED_IMPLEMENTATION_ROADMAP.md پڑھو
→ پھر PHASE 1 - Item 1.1 سے شروع کرو

❓ Item کی تفصیلات کہاں ہیں؟
→ IMPLEMENTATION_DETAILS_GUIDE.md میں ہیں
→ ہر item کے لیے step-by-step ہے

❓ کیا parallel کر سکتا ہوں؟
→ PHASE 1: نہیں (sequential فقط)
→ PHASE 2: ہاں (لیکن اگر PHASE 1 done ہو)
→ PHASE 3: ہاں (لیکن اگر PHASE 2 done ہو)

❓ ایک item fail ہو تو؟
→ اسے fix کرو
→ دوبارہ test کرو
→ پھر اگلی item

❓ Code مثالیں کہاں ہیں؟
→ IMPLEMENTATION_DETAILS_GUIDE.md میں
→ Copy-paste ready ہے

❓ Tests کہاں ہیں؟
→ ہر item میں test details ہے
→ IMPLEMENTATION_DETAILS_GUIDE.md میں
```

---

## 🚨 اہم نکات

### ❌ مت کرو:
```
❌ Parallel work in PHASE 1
❌ Skip verification steps
❌ Jump to PHASE 2 before PHASE 1 done
❌ Ignore test failures
❌ Commit broken code
❌ غیر sequence میں کام کرو
```

### ✅ ہمیشہ کرو:
```
✅ Follow sequence exactly
✅ Verify each item completely
✅ Run tests before moving on
✅ Commit with proper messages
✅ Report progress clearly
✅ تمام checklist items complete کرو
```

---

## 📊 Progress Reporting

```
ہر item مکمل ہونے پر:

"✅ PHASE X - Item X.X COMPLETED
   Files: [list]
   Changes: [brief]
   Tests: PASSED
   Status: Ready for next item"
```

---

## 🎯 Final Target

```
Goal: پروجیکٹ کو 100% صاف اور کام کرنے والا بنانا

Timeline:
  - PHASE 1: 2-3 hours (روز 1)
  - PHASE 2: 4-6 hours (روز 2-3)
  - PHASE 3: 2-3 hours (روز 4+)
  ─────────────────────────
  Total: 8-12 hours

Outcome:
  ✅ تمام 12 issues fixed
  ✅ تمام tests passing
  ✅ Documentation accurate
  ✅ Code ready for deployment
```

---

## 🚀 شروع کرو

```
اب یہ کرو:

1. PHASED_IMPLEMENTATION_ROADMAP.md کھولو
2. PHASE 1 - Item 1.1 سے شروع کرو
3. IMPLEMENTATION_DETAILS_GUIDE.md reference کرو
4. Steps follow کرو
5. Complete کرو اور report دو
6. PHASE 1 دوسری items کرو
7. پھر PHASE 2
8. آخر میں PHASE 3

تم یہ کر سکتے ہو! 💪
```

---

**یہ پرامپت final ہے۔ اب شروع کر!**

