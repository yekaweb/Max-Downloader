"""
Music Recognition Service using ShazamIO and audio signal processing.
Provides intelligent music identification (Shazam-style) for social media media.
Supports ambient/background music detection with voice attenuation filtering.
"""

import os
import re
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from shazamio import Shazam

logger = logging.getLogger(__name__)


class MusicRecognitionService:
    """
    AI-powered audio recognition engine for identifying songs, background music,
    and soundtrack metadata from audio/video streams.
    """

    def __init__(self):
        self.shazam = Shazam()
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def recognize_audio(
        self,
        audio_path: Path,
        try_enhancement: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Identify song from an audio/video file.
        
        Steps:
        1. Direct signature recognition via ShazamIO.
        2. If not found and try_enhancement is True:
           Applies center-channel vocal reduction and bandpass filter,
           then retries Shazam recognition.
        """
        if not audio_path or not audio_path.exists():
            logger.warning(f"[MusicRecognition] File not found: {audio_path}")
            return None

        # 1. Direct Recognition
        try:
            logger.info(f"[MusicRecognition] Attempting direct Shazam on {audio_path.name}")
            out = await self.shazam.recognize(str(audio_path))
            track = out.get("track")
            if track:
                result = self._format_track_data(track)
                logger.info(f"[MusicRecognition] Direct match found: {result.get('title')} - {result.get('artist')}")
                return result
        except Exception as e:
            logger.warning(f"[MusicRecognition] Direct recognition error: {e}")

        # 2. Audio Enhancement for Background Music / Spoken Voice Over Music
        if try_enhancement:
            enhanced_path = audio_path.parent / f"enh_{audio_path.stem}.mp3"
            try:
                logger.info(f"[MusicRecognition] Attempting audio vocal-filtering enhancement for {audio_path.name}")
                success = await self._enhance_background_audio(audio_path, enhanced_path)
                if success and enhanced_path.exists():
                    out_enh = await self.shazam.recognize(str(enhanced_path))
                    track_enh = out_enh.get("track")
                    if track_enh:
                        result = self._format_track_data(track_enh)
                        logger.info(f"[MusicRecognition] Enhanced match found: {result.get('title')} - {result.get('artist')}")
                        return result
            except Exception as enh_err:
                logger.warning(f"[MusicRecognition] Enhancement recognition error: {enh_err}")
            finally:
                if enhanced_path.exists():
                    try:
                        enhanced_path.unlink()
                    except Exception:
                        pass

        logger.info(f"[MusicRecognition] No track match found for {audio_path.name}")
        return None

    async def _enhance_background_audio(self, src_path: Path, dst_path: Path) -> bool:
        """
        Apply audio filters using FFmpeg to reduce dominant foreground speech
        and amplify background rhythmic/harmonic frequencies.
        """
        from utils.ffmpeg_utils import apply_audio_filter
        af_filter = "highpass=f=200,lowpass=f=4500,volume=1.8,acompressor=threshold=-18dB:ratio=4:attack=20:release=250"
        return await apply_audio_filter(src_path, dst_path, af_filter, bitrate="192k")

    def _format_track_data(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract clean, human-readable metadata from Shazam raw track dictionary.
        """
        title = track.get("title", "Unknown Title")
        artist = track.get("subtitle", "Unknown Artist")
        
        # Album name
        sections = track.get("sections", [])
        album = "Single / Unknown Album"
        release_year = ""
        label = ""
        for sec in sections:
            if sec.get("type") == "SONG":
                for metadata in sec.get("metadata", []):
                    title_type = metadata.get("title", "").lower()
                    if "album" in title_type:
                        album = metadata.get("text", album)
                    elif "released" in title_type or "year" in title_type:
                        release_year = metadata.get("text", "")
                    elif "label" in title_type:
                        label = metadata.get("text", "")

        # Genre
        genres = track.get("genres", {}).get("primary", "")

        # Images / Cover
        images = track.get("images", {})
        cover_url = images.get("coverarthq") or images.get("coverart") or images.get("background") or ""

        # Streaming / External links
        share = track.get("share", {})
        shazam_url = share.get("href") or share.get("html") or ""
        
        # Spotify & YouTube search links
        query_encoded = f"{artist} {title}".replace(" ", "+")
        spotify_search_url = f"https://open.spotify.com/search/{query_encoded}"
        youtube_search_url = f"https://www.youtube.com/results?search_query={query_encoded}"

        return {
            "title": title,
            "artist": artist,
            "album": album,
            "genre": genres,
            "release_year": release_year,
            "label": label,
            "cover_url": cover_url,
            "shazam_url": shazam_url,
            "spotify_url": spotify_search_url,
            "youtube_url": youtube_search_url,
            "search_query": f"{artist} - {title}",
            "raw": track,
        }


music_recognition_service = MusicRecognitionService()

__all__ = ["MusicRecognitionService", "music_recognition_service"]
