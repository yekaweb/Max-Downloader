import os

cookie_path = "cookies.txt"

if not os.path.exists(cookie_path):
    print("❌ فایل cookies.txt پیدا نشد!")
    exit(1)

with open(cookie_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
fixed_count = 0

for line in lines:
    if line.startswith("#HttpOnly_"):
        new_lines.append(line.replace("#HttpOnly_", ""))
        fixed_count += 1
    else:
        new_lines.append(line)

with open(cookie_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"✅ فایل cookies.txt تعمیر شد! تعداد {fixed_count} خط که به دلیل HttpOnly بودن توسط yt-dlp نادیده گرفته می‌شدند اصلاح شدند.")
print("حالا ربات را ری‌استارت کنید: sudo docker compose restart")
