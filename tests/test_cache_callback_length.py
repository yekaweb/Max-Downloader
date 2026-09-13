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


def test_video_quality_and_codec_keyboards():
    from bot.keyboards.inline.download import get_video_quality_keyboard, get_video_codec_keyboard
    
    mock_format_info = {
        "video_formats": {
            "4k": {"size_mb": 619.0},
            "1440p": {"size_mb": 278.1},
            "1080p": {"size_mb": 133.9},
            "720p": {"size_mb": 74.7},
            "480p": {"size_mb": 49.5},
            "360p": {"size_mb": 39.0},
            "240p": {"size_mb": 27.3},
            "144p": {"size_mb": 24.0},
        },
        "codec_sizes": {
            "h264": {"size_mb": 74.7},
            "av1": {"size_mb": 60.2},
            "vp9": {"size_mb": 65.1},
        }
    }
    
    q_kb = get_video_quality_keyboard(mock_format_info)
    assert len(q_kb.inline_keyboard) == 9  # 8 qualities + 1 back button
    for row in q_kb.inline_keyboard:
        for btn in row:
            assert len(btn.callback_data.encode('utf-8')) <= 64
            
    c_kb = get_video_codec_keyboard(mock_format_info["codec_sizes"])
    assert len(c_kb.inline_keyboard) == 4  # 3 codecs + 1 back button
    for row in c_kb.inline_keyboard:
        for btn in row:
            assert len(btn.callback_data.encode('utf-8')) <= 64
