"""
AI Persian Dubbing & Vocal Synthesis Service for DLBot.
Converts subtitles / translated scripts to natural Persian vocal tracks using Edge-TTS Neural voices
and mixes them into the video container via FFmpeg.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import edge_tts

logger = logging.getLogger(__name__)

FA_VOICE_MALE = "fa-IR-FaridNeural"
FA_VOICE_FEMALE = "fa-IR-DilaraNeural"


class AiDubbingService:
    """
    Synthesizes Persian audio and merges it into videos.
    """

    def __init__(self, temp_dir: str = "temp_downloads"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_persian_audio(
        self,
        text: str,
        output_audio_path: Path,
        voice: str = FA_VOICE_MALE,
        rate: str = "+0%",
    ) -> Path:
        """
        Generate MP3 audio file from Persian text using Microsoft Neural TTS.
        """
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(str(output_audio_path))
        return output_audio_path

    async def dub_video(
        self,
        video_path: Path,
        dubbed_audio_path: Path,
        output_path: Path,
        mix_original_volume: float = 0.15,
    ) -> Path:
        """
        Mix Persian dubbed audio over original video with background ducking.
        If mix_original_volume == 0, replaces original audio entirely.
        """
        if mix_original_volume == 0:
            # Complete audio replacement (fast stream copy for video)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(dubbed_audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_path),
            ]
        else:
            # Audio ducking: original audio at lower volume + dubbed voice at full volume
            filter_complex = (
                f"[0:a]volume={mix_original_volume}[orig];"
                f"[1:a]volume=1.0[dub];"
                f"[orig][dub]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(dubbed_audio_path),
                "-filter_complex", filter_complex,
                "-map", "0:v:0",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(output_path),
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"FFmpeg dubbing failed: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg dubbing failed with code {proc.returncode}")

        return output_path


ai_dubbing_service = AiDubbingService()

__all__ = ["AiDubbingService", "ai_dubbing_service", "FA_VOICE_MALE", "FA_VOICE_FEMALE"]
