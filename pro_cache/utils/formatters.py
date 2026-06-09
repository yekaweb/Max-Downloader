"""
Utility formatters for Pro Cache
توابع کمکی برای فرمت کردن داده‌ها
"""

from typing import Union
from datetime import timedelta


def format_file_size(size_bytes: Union[int, float]) -> str:
    """
    تبدیل حجم فایل به فرمت خوانا
    
    Args:
        size_bytes: حجم فایل به بایت
        
    Returns:
        رشته فرمت شده مثل "25.5 MB"
    """
    if size_bytes < 0:
        return "نامعلوم"
    
    # تعریف واحدها
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    # فرمت کردن بر اساس حجم
    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    elif size >= 100:  # برای اعداد بزرگ، بدون اعشار
        return f"{int(size)} {units[unit_index]}"
    elif size >= 10:  # یک رقم اعشار
        return f"{size:.1f} {units[unit_index]}"
    else:  # دو رقم اعشار برای اعداد کوچک
        return f"{size:.2f} {units[unit_index]}"


def format_duration(seconds: Union[int, float, None]) -> str:
    """
    تبدیل زمان به فرمت خوانا
    
    Args:
        seconds: مدت زمان به ثانیه
        
    Returns:
        رشته فرمت شده مثل "12:34" یا "1:23:45"
    """
    if seconds is None or seconds < 0:
        return "نامعلوم"
    
    # تبدیل به int
    total_seconds = int(seconds)
    
    # محاسبه ساعت، دقیقه و ثانیه
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # فرمت کردن بر اساس مدت زمان
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def format_number(number: Union[int, float]) -> str:
    """
    فرمت کردن اعداد با جداکننده هزارگان
    
    Args:
        number: عدد ورودی
        
    Returns:
        رشته فرمت شده مثل "1,234,567"
    """
    if isinstance(number, float):
        # برای اعداد اعشاری
        if number.is_integer():
            return f"{int(number):,}"
        else:
            return f"{number:,.2f}"
    else:
        return f"{number:,}"


def format_percentage(value: float, total: float) -> str:
    """
    محاسبه و فرمت کردن درصد
    
    Args:
        value: مقدار فعلی
        total: مقدار کل
        
    Returns:
        رشته فرمت شده مثل "45.6%"
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    
    if percentage == 100:
        return "100%"
    elif percentage >= 10:
        return f"{percentage:.1f}%"
    else:
        return f"{percentage:.2f}%"


def format_speed(bytes_per_second: float) -> str:
    """
    فرمت کردن سرعت دانلود/آپلود
    
    Args:
        bytes_per_second: سرعت به بایت بر ثانیه
        
    Returns:
        رشته فرمت شده مثل "2.5 MB/s"
    """
    if bytes_per_second <= 0:
        return "0 B/s"
    
    size_text = format_file_size(bytes_per_second)
    return f"{size_text}/s"


def format_time_ago(seconds_ago: int) -> str:
    """
    نمایش زمان به صورت "چند وقت پیش"
    
    Args:
        seconds_ago: تعداد ثانیه‌های گذشته
        
    Returns:
        رشته فرمت شده مثل "5 دقیقه پیش"
    """
    if seconds_ago < 0:
        return "در آینده!"
    
    if seconds_ago < 60:
        return "همین الان"
    
    minutes = seconds_ago // 60
    if minutes < 60:
        if minutes == 1:
            return "1 دقیقه پیش"
        return f"{minutes} دقیقه پیش"
    
    hours = minutes // 60
    if hours < 24:
        if hours == 1:
            return "1 ساعت پیش"
        return f"{hours} ساعت پیش"
    
    days = hours // 24
    if days < 30:
        if days == 1:
            return "دیروز"
        return f"{days} روز پیش"
    
    months = days // 30
    if months < 12:
        if months == 1:
            return "1 ماه پیش"
        return f"{months} ماه پیش"
    
    years = months // 12
    if years == 1:
        return "1 سال پیش"
    return f"{years} سال پیش"


def format_eta(seconds_remaining: int) -> str:
    """
    فرمت کردن زمان باقیمانده
    
    Args:
        seconds_remaining: ثانیه‌های باقیمانده
        
    Returns:
        رشته فرمت شده مثل "5 دقیقه و 30 ثانیه"
    """
    if seconds_remaining <= 0:
        return "تکمیل شده"
    
    td = timedelta(seconds=seconds_remaining)
    
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    
    parts = []
    
    if days > 0:
        parts.append(f"{days} روز")
    if hours > 0:
        parts.append(f"{hours} ساعت")
    if minutes > 0:
        parts.append(f"{minutes} دقیقه")
    if seconds > 0 and not parts:  # فقط اگر کمتر از یک دقیقه بود
        parts.append(f"{seconds} ثانیه")
    
    if len(parts) == 0:
        return "کمتر از 1 ثانیه"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} و {parts[1]}"
    else:
        return f"{parts[0]}، {parts[1]} و {parts[2]}"


def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """
    ایجاد نوار پیشرفت متنی
    
    Args:
        current: مقدار فعلی
        total: مقدار کل
        length: طول نوار پیشرفت
        
    Returns:
        رشته نوار پیشرفت مثل "[████████░░░░░░░░░░░░]"
    """
    if total == 0:
        return "[" + "░" * length + "]"
    
    progress = min(current / total, 1.0)
    filled = int(length * progress)
    empty = length - filled
    
    return "[" + "█" * filled + "░" * empty + "]"


def format_quality_info(quality_data: dict) -> str:
    """
    فرمت کردن اطلاعات کیفیت برای نمایش
    
    Args:
        quality_data: دیکشنری حاوی اطلاعات کیفیت
        
    Returns:
        رشته فرمت شده اطلاعات کیفیت
    """
    parts = []
    
    # کیفیت/رزولوشن
    if quality_data.get('quality_label'):
        parts.append(quality_data['quality_label'])
    elif quality_data.get('resolution'):
        parts.append(quality_data['resolution'])
    
    # کدک
    if quality_data.get('video_codec'):
        parts.append(quality_data['video_codec'].upper())
    
    # فرمت
    if quality_data.get('extension'):
        parts.append(quality_data['extension'].upper())
    
    # حجم
    if quality_data.get('file_size'):
        size = format_file_size(quality_data['file_size'])
        parts.append(size)
    
    # FPS
    if quality_data.get('fps'):
        parts.append(f"{quality_data['fps']}fps")
    
    return " • ".join(parts)


# تست formatters
if __name__ == "__main__":
    # تست format_file_size
    print("File sizes:")
    print(format_file_size(0))  # 0 B
    print(format_file_size(1023))  # 1023 B
    print(format_file_size(1024))  # 1.00 KB
    print(format_file_size(1536))  # 1.50 KB
    print(format_file_size(1048576))  # 1.00 MB
    print(format_file_size(1073741824))  # 1.00 GB
    
    # تست format_duration
    print("\nDurations:")
    print(format_duration(45))  # 0:45
    print(format_duration(125))  # 2:05
    print(format_duration(3665))  # 1:01:05
    
    # تست format_time_ago
    print("\nTime ago:")
    print(format_time_ago(30))  # همین الان
    print(format_time_ago(180))  # 3 دقیقه پیش
    print(format_time_ago(7200))  # 2 ساعت پیش
    print(format_time_ago(259200))  # 3 روز پیش