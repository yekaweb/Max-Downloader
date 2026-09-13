"""
Test to ensure all Telegram inline keyboard callback_data payloads strictly respect
Telegram's 64-byte limitation (preventing BUTTON_DATA_INVALID errors).
"""

from bot.keyboards.inline.cache_keyboards import get_cache_options_keyboard, get_cached_qualities_keyboard
from database.models.cached_download import CachedQuality


def test_cache_options_keyboard_callback_length():
    # Test with normal cache_id
    kb = get_cache_options_keyboard(quality_count=3, cache_id=123)
    for row in kb.inline_keyboard:
        for btn in row:
            assert btn.callback_data is not None
            assert len(btn.callback_data.encode('utf-8')) <= 64, (
                f"Button '{btn.text}' callback_data '{btn.callback_data}' exceeds 64 bytes!"
            )


def test_cached_qualities_keyboard_callback_length():
    mock_qualities = [
        CachedQuality(id=1, cache_id=123, quality_label="1080p", telegram_file_id="BAACAgIAAxk...", mime_type="video/mp4", extension="mp4", file_size=104857600),
        CachedQuality(id=2, cache_id=123, quality_label="720p", telegram_file_id="BAACAgIAAxk...", mime_type="video/mp4", extension="mp4", file_size=52428800),
        CachedQuality(id=3, cache_id=123, quality_label="MP3 320kbps", telegram_file_id="BAACAgIAAxk...", mime_type="audio/mp3", extension="mp3", file_size=10485760),
    ]
    kb = get_cached_qualities_keyboard(mock_qualities, show_back=True)
    for row in kb.inline_keyboard:
        for btn in row:
            assert btn.callback_data is not None
            assert len(btn.callback_data.encode('utf-8')) <= 64, (
                f"Button '{btn.text}' callback_data '{btn.callback_data}' exceeds 64 bytes!"
            )
