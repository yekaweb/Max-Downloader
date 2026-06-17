import yt_dlp
import os

# Set cache dir to our persistent volume
cache_dir = '/app/cached_files/yt_dlp_cache'
os.makedirs(cache_dir, exist_ok=True)

ydl_opts = {
    'username': 'oauth2',
    'password': '',
    'cachedir': cache_dir,
    'quiet': False,
    'extractor_args': {
        'youtube': {
            'player_client': ['web', 'android', 'ios'],
        }
    }
}

print("\n" + "="*60)
print("🚀 YouTube OAuth2 Authentication System")
print("="*60)
print("\nدر حال ارتباط با سرورهای گوگل...")
print("لطفاً به پیام بعدی دقت کنید. گوگل یک لینک و یک کد به شما می‌دهد.")
print("باید با فیلترشکن وارد لینک شوید، کد را وارد کنید و به ربات دسترسی بدهید.")
print("\n" + "="*60 + "\n")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # We just extract info from a tiny video to trigger the auth flow
        ydl.extract_info("https://www.youtube.com/watch?v=BaW_jenozKc", download=False)
        print("\n✅ احراز هویت با موفقیت انجام شد! توکن در سرور ذخیره شد.")
        print("حالا می‌توانید فایل cookies.txt را پاک کنید و ربات را با بالاترین کیفیت‌ها استفاده کنید!")
except Exception as e:
    print(f"\n❌ خطا در عملیات: {e}")
