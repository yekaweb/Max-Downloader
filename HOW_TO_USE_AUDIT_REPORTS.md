# 📖 راهنمای استفاده از گزارش‌های اشکال‌زدایی

> **این فایل توضیح می‌دهد که چطور از گزارش‌های تازه‌ایجاد شده استفاده کنید**

---

## 🎯 سه فایل منتشر شده است:

### 1️⃣ **PROJECT_AUDIT_ANALYSIS.md** (34KB)
- ✅ **برای کی**: Developers، Architects، Code Reviewers
- ✅ **محتوا**: تمام 12 ایراد + راه‌حل‌های دقیق + کد examples
- ✅ **زمان خواندن**: 30-45 دقیقه
- ✅ **استفاده**: هر ایراد برای implementation ready است

**مثال بخش**:
```markdown
### **5️⃣ مشکل Database Migrations — Alembic Setup ناقص**

#### 🔴 **مشکل**: ...
#### ✅ **راه‌حل**: 
```python
# کد آماده‌برای copy/paste
```
```

---

### 2️⃣ **QUICK_AUDIT_CHECKLIST.md** (6KB)
- ✅ **برای کی**: Managers، Team Leads، Quick Decision Making
- ✅ **محتوا**: Checklist سریع + اولویت‌بندی + timeline
- ✅ **زمان خواندن**: 5-10 دقیقه
- ✅ **استفاده**: Task assignment و sprint planning

**استفاده در جلسات**:
```
- Sprint 1 (روز 1): 3 ایراد بحرانی
- Sprint 2 (روز 2-3): 7 ایراد متوسط  
- Sprint 3 (روز 4+): 2 ایراد کم
```

---

### 3️⃣ **HOW_TO_USE_AUDIT_REPORTS.md** (این فایل)
- ✅ **برای کی**: همه
- ✅ **محتوا**: راهنمای استفاده و workflow
- ✅ **زمان خواندن**: 5 دقیقه
- ✅ **استفاده**: شروع کردن

---

## 🚀 کار با گزارش‌ها

### **سناریو 1: شما یک Developer هستید**

#### ✅ مرحله 1: خود را معرّفی کنید
```bash
git config user.name "نام شما"
git config user.email "email@example.com"
```

#### ✅ مرحله 2: بخش شامل ایراد را بخوانید
```markdown
# گزارش را باز کنید: PROJECT_AUDIT_ANALYSIS.md

# برو به بخش: "### **5️⃣ مشکل CachedFile Model**"

# کل بخش را بخوانید:
- مشکل چیست
- کدام خطوط کد اشکالی دارند
- راه‌حل دقیق چیست
```

#### ✅ مرحله 3: راه‌حل را پیاده‌سازی کنید
```bash
# 1. فایل مورد نظر را باز کنید
vim database/models/cached_file.py

# 2. کد جدید را copy/paste کنید (از گزارش)

# 3. تست کنید
python -m pytest tests/test_models.py

# 4. Commit کنید
git commit -m "Fix: Add unique constraint to CachedFile model"
```

---

### **سناریو 2: شما یک Architect/Lead هستید**

#### ✅ مرحله 1: خلاصه بخوانید
```markdown
# باز کنید: QUICK_AUDIT_CHECKLIST.md

# نگاه کنید به جدول:
| # | ایراد | شدت | حل |
|---|-------|------|-----|

# اینجا priority اول است
```

#### ✅ مرحله 2: Task‌ها assign کنید
```
🔴 بحرانی (روز 1):
  ├─ Developer_A: "Fix syntax errors in We want build this.md"
  ├─ Developer_B: "Create PROJECT_ACTUAL_STATUS.md"  
  └─ Developer_C: "Create STRUCTURE_VERIFICATION.md"

🟡 متوسط (روز 2-3):
  ├─ Specialist_1: "Fix ModuleRegistry priority"
  ├─ Specialist_2: "Add CachedFile unique constraints"
  ├─ Specialist_3: "Implement Progress throttling"
  └─ ...
```

#### ✅ مرحله 3: پیشرفت تتبع کنید
```bash
# روزانه:
- کدام task‌ها done شدند؟
- کدام task‌ها blocked شده‌اند?
- نیاز به help دارد؟

# واقع تو گزارش:
PROJECT_AUDIT_ANALYSIS.md:
  ✅ Issue #1: DONE (2026-05-28)
  ✅ Issue #2: DONE (2026-05-28)
  🔄 Issue #3: IN_PROGRESS (started 2026-05-28)
  ❌ Issue #4: PENDING
```

---

### **سناریو 3: شما یک AI Agent هستید (Cursor/GPT)**

#### ✅ مرحله 1: Audit بخش را فهمید
```python
# User می‌گوید:
# "Fix issue #5 in PROJECT_AUDIT_ANALYSIS.md"

# شما:
# 1. فایل را باز می‌کنید
# 2. بخش "### **5️⃣" را می‌خوانید
# 3. کد example را می‌گیرید
# 4. فایل source را ویرایش می‌کنید
# 5. Test می‌کنید
```

#### ✅ مرحله 2: Multiple Issues همزمان
```python
# اگر user می‌گوید: "Fix all critical issues"

# شما:
items = QUICK_AUDIT_CHECKLIST[severity='🔴']
for item in items:
    read_section(f"PROJECT_AUDIT_ANALYSIS.md#{item.number}")
    implement_solution(item)
    test_solution(item)
    report_status(item)
```

#### ✅ مرحله 3: Parallel work
```
Agent_1 → Issue #1
Agent_2 → Issue #2  
Agent_3 → Issue #3
================
All done in parallel, report to team
```

---

## 📋 Workflow پیشنهادی

### **روز 1: Documentation & Planning**
```
9:00-10:00:  Team meeting
  ├─ Discuss audit findings
  ├─ Assign critical issues
  └─ Timeline agreement

10:00-12:00: Documentation fixes
  ├─ Fix syntax errors
  ├─ Create PROJECT_ACTUAL_STATUS.md
  └─ Verify structure

14:00-17:00: Development (parallel)
  └─ Start first set of issues
```

### **روز 2-3: Implementation**
```
Focus on 🟡 Medium priority issues
- Each developer: 1-2 issues
- Daily standup: 15 min check-in
- Code review: 1-2 hours
```

### **روز 4+: Polish & Optimize**
```
Focus on 🟢 Low priority issues
- Tests & coverage
- Documentation
- Performance optimization
```

---

## 🔍 چطور هر گزارش کار می‌کند؟

### **PROJECT_AUDIT_ANALYSIS.md**

```
📌 Structure:
├─ Header (Purpose, Date)
├─ Checklist of reviewed files
├─ 12 Issues detailed sections
│  ├─ 🔴 Issue explanation
│  ├─ ❌ Problems identified
│  ├─ ✅ Solution detailed
│  └─ 📝 Code examples
└─ Summary table
└─ Next steps

🎯 Use this when:
- Implementing specific issue
- Understanding root cause
- Code reviewing fixes
- Training new team members
```

### **QUICK_AUDIT_CHECKLIST.md**

```
📌 Structure:
├─ Executive summary
├─ 12 Issues quick overview
│  ├─ Severity level
│  ├─ Short description
│  └─ Quick fix indicator
├─ Priority table
├─ Execution order
└─ Team assignment guide

🎯 Use this when:
- Planning sprint
- Assigning tasks
- Status reporting
- Making quick decisions
```

### **HOW_TO_USE_AUDIT_REPORTS.md** (اینجا)

```
📌 Structure:
├─ Overview of 3 documents
├─ Scenarios (Developer/Lead/Agent)
├─ Workflow suggestions
├─ File usage guide
└─ FAQ

🎯 Use this when:
- Starting implementation
- Team orientation
- Workflow questions
- Clarifying roles
```

---

## ❓ FAQ

### **Q: از کدام فایل شروع کنم؟**
A: اگر شما:
- **Developer**: `PROJECT_AUDIT_ANALYSIS.md` (بخش شامل ایراد شما)
- **Manager**: `QUICK_AUDIT_CHECKLIST.md`
- **New**: `HOW_TO_USE_AUDIT_REPORTS.md` (اینجا)

---

### **Q: چطور اگر یک ایراد بزرگ‌تر است؟**
A: تقسیم کنید:
1. بخش مربوطه در `PROJECT_AUDIT_ANALYSIS.md` را پیدا کنید
2. "راه‌حل" بخش را به کوچک‌تر task‌ها تقسیم کنید
3. ترتیب وابستگی‌ها تصدیق کنید
4. Implement کنید step-by-step

---

### **Q: اگر ایراد‌های دیگری پیدا کردم؟**
A:
1. آن را document کنید (like in PROJECT_AUDIT_ANALYSIS.md)
2. Add کنید به **issue list**
3. Set priority (🔴/🟡/🟢)
4. Assign و implement کنید

---

### **Q: چطور test کنم که fix درست است؟**
A: هر ایراد در گزارش **expected outcome** دارد:

```markdown
### Fix: Add unique constraint
✅ Expected:
  - CachedFile model has __unique_constraint__
  - Duplicate entries impossible
  - Migration created successfully
  - Tests pass for constraint validation

Test:
  pytest tests/test_models.py::test_cached_file_unique
```

---

### **Q: توتر parallel کار کنم یا sequential؟**
A: **Hybrid** approach:
- 🔴 Critical issues: Sequential (1 per sprint)
- 🟡 Medium issues: Parallel (2-3 per sprint)  
- 🟢 Low issues: Parallel (4+ per sprint)

**مثال Timeline**:
```
Sprint 1 (Parallel):
├─ Dev_A → Issue #1 (Critical)
├─ Dev_B → Issue #2 (Critical)  
└─ Dev_C → Issue #3 (Critical)

Sprint 2 (Parallel):
├─ Dev_A → Issue #4 (Medium)
├─ Dev_B → Issue #5 (Medium)
├─ Dev_C → Issue #6 (Medium)
└─ Dev_D → Issue #7 (Medium)
```

---

## 🎓 Team Training

### **برای Onboarding New Members**:
```
1. "راهنما را بخوانید" (این فایل)
2. "Quick checklist" را نگاه کنید
3. "یک ایراد" انتخاب کنید
4. "Detailed section" را بخوانید  
5. "Solution" را پیاده‌سازی کنید
6. "Code review" دریافت کنید
7. Repeat → حالا expert هستید!
```

---

## 📊 Progress Tracking

### **Daily Standup Template**:
```
Today's Done:
- ✅ Issue #X (100%)
- ✅ Issue #Y (75%)

Blocked:
- ❌ Issue #Z (needs DB reset)

Tomorrow:
- Issue #A (estimated 4h)
- Issue #B (estimated 2h)
```

### **Weekly Summary**:
```
Week Summary:
- Total Issues: 12
- Completed: 3 (25%)
- In Progress: 4 (33%)
- Blocked: 1 (8%)
- Not Started: 4 (34%)

Timeline on track? YES/NO
Any risks? ...
```

---

## ✅ نکات نهایی

### **برای بهترین نتایج**:
1. ✅ **Read completely** گزارش مربوطه را
2. ✅ **Understand context** قبل از implement
3. ✅ **Copy code examples** از گزارش
4. ✅ **Test thoroughly** بعد از هر تغیر
5. ✅ **Document changes** برای دیگران
6. ✅ **Report progress** روزانه/هفتگی

### **Red Flags to Watch**:
```
❌ "I don't understand the issue" 
   → Re-read detailed section or ask team

❌ "Solution seems incomplete"
   → Check code examples and comments

❌ "Test failing after fix"
   → Review expected outcome in report

❌ "Blocking other tasks"
   → Report immediately to team lead
```

---

## 🤝 Support Resources

- **Detailed Analysis**: `PROJECT_AUDIT_ANALYSIS.md`
- **Quick Reference**: `QUICK_AUDIT_CHECKLIST.md`
- **Architecture Docs**: `ROADMAP.md`, `README.md`
- **Original Spec**: `We want build this.md`

---

**نوشته شده**: 2026-05-28  
**ورژن**: 1.0  
✅ آماده استفاده از امروز!

---

> **نکته مهم**: اگر سؤالی دارید یا confusion پیدا کردید، این یک **sign** است که documentation بیشتر نیاز دارد. لطفاً issue open کنید! 🎯
