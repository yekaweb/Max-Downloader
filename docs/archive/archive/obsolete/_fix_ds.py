"""Fix download_service.py for new two-table model"""
target = r"D:\Max Downloader\Max-Downloader\services\download_service.py"
with open(target, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix: telegram_file_id is now on CachedQuality, not CachedDownload
old = '"telegram_file_id": entry.telegram_file_id'
new = '"telegram_file_id": first_quality.telegram_file_id if first_quality else None'
c = c.replace(old, new)

old2 = 'entry = cached[0]'
new2 = 'entry = cached[0]\n                    first_quality = entry.qualities[0] if entry.qualities else None'
c = c.replace(old2, new2)

with open(target, 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed download_service.py")