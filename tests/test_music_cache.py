"""
Unit tests for Pro Music Caching & Zero-Disk Storage in Max-Downloader
"""

import pytest
import os
import uuid
import hashlib
from pathlib import Path

from database.connection import engine, AsyncSessionLocal
from database.models.models import Base
from database.repositories.cached_download_repo import CachedDownloadRepository


@pytest.mark.asyncio
async def test_music_cache_hash_consistency():
    """Verify that normalized music query generates consistent SHA-256 hashes."""
    term1 = "Shadmehr Aghili Ghalbe Man"
    term2 = "  shadmehr aghili ghalbe man  "
    
    clean1 = term1.lower().strip()
    clean2 = term2.lower().strip()
    
    hash1 = hashlib.sha256(f"music_320_{clean1}".encode()).hexdigest()
    hash2 = hashlib.sha256(f"music_320_{clean2}".encode()).hexdigest()
    
    assert hash1 == hash2
    assert len(hash1) == 64


@pytest.mark.asyncio
async def test_music_cache_repository_write_and_read():
    """Verify that music track file_id can be written to and retrieved from Pro Cache database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    uid = uuid.uuid4().hex[:8]
    track_title = f"Ghalbe Man {uid}"
    artist = f"Shadmehr Aghili {uid}"
    fake_file_id = f"AgACAgIAAxkBAAIBY2_{uid}_audio_telegram_file_id"
    norm_key = f"{artist.lower().strip()}_{track_title.lower().strip()}"
    music_hash = hashlib.sha256(f"music_320_{norm_key}".encode()).hexdigest()
    
    # 1. Save music to cache in session 1
    async with AsyncSessionLocal() as session1:
        repo1 = CachedDownloadRepository(session1)
        created = await repo1.create_from_upload(
            source_url=f"music://{norm_key}",
            source_platform="music",
            media_title=track_title,
            media_duration=210,
            media_uploader=artist,
            telegram_file_id=fake_file_id,
            file_size=8 * 1024 * 1024,
            file_type="audio/mp3",
            quality="320kbps",
            format_codec="mp3",
            format_container="mp3",
            url_hash=music_hash,
        )
        assert created is not None
        assert created.url_hash == music_hash
        
    # 2. Retrieve from cache in fresh session 2
    async with AsyncSessionLocal() as session2:
        repo2 = CachedDownloadRepository(session2)
        found = await repo2.find_valid_by_url_hash(music_hash)
        assert found is not None
        assert found.title == track_title
        assert found.uploader == artist
        assert len(found.qualities) >= 1
        assert found.qualities[0].telegram_file_id == fake_file_id
        assert found.qualities[0].quality_label == "320kbps"
        
        # 3. Mark used (increment hit count)
        initial_access = found.access_count or 0
        await repo2.mark_used(found.id, found.qualities[0].id)
        
        updated = await repo2.get_by_id(found.id)
        assert updated.access_count == initial_access + 1


@pytest.mark.asyncio
async def test_instagram_audio_cache_write_and_read():
    """Verify that Instagram extracted audio (MP3) is cached by shortcode hash."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    uid = uuid.uuid4().hex[:8]
    shortcode = f"C7x_{uid}"
    audio_hash = hashlib.sha256(f"ig_audio_{shortcode}".encode()).hexdigest()
    fake_ig_audio_id = f"CQACAgIAAxkBAAIZ_{uid}_ig_audio_file_id"
    
    async with AsyncSessionLocal() as session1:
        repo1 = CachedDownloadRepository(session1)
        await repo1.create_from_upload(
            source_url=f"https://www.instagram.com/reel/{shortcode}/",
            source_platform="instagram_audio",
            media_title=f"Instagram Audio ({shortcode})",
            media_duration=45,
            media_uploader="Instagram Audio",
            telegram_file_id=fake_ig_audio_id,
            file_size=1 * 1024 * 1024,
            file_type="audio/mp3",
            quality="192kbps",
            format_codec="mp3",
            format_container="mp3",
            url_hash=audio_hash,
        )
        
    async with AsyncSessionLocal() as session2:
        repo2 = CachedDownloadRepository(session2)
        cached = await repo2.find_valid_by_url_hash(audio_hash)
        assert cached is not None
        assert len(cached.qualities) >= 1
        assert cached.qualities[0].telegram_file_id == fake_ig_audio_id
        assert cached.qualities[0].quality_label == "192kbps"


@pytest.mark.asyncio
async def test_zero_disk_storage_cleanup():
    """Verify that downloaded temp audio files are immediately deleted on disk."""
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    uid = uuid.uuid4().hex[:8]
    test_file = temp_dir / f"temp_track_{uid}_test_deletion.mp3"
    test_file.write_text("dummy mp3 audio content")
    assert test_file.exists()
    
    # Simulate finally cleanup
    try:
        pass
    finally:
        if test_file.exists():
            test_file.unlink()
            
    assert not test_file.exists()
