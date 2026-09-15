"""
Centralized FFmpeg execution utilities with robust error handling and structured logging.
Uses thread-pool execution to avoid asyncio child watcher issues across Python versions.
"""

import os
import asyncio
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple
from loguru import logger


def _run_ffmpeg_sync(cmd: List[str], timeout: int = 120) -> Tuple[bool, str, str]:
    """Synchronously execute an FFmpeg command with timeout and output capture."""
    start_time = time.time()
    cmd_str = " ".join(cmd)
    logger.debug(f"[FFmpeg] Executing: {cmd_str}")
    
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        elapsed = time.time() - start_time
        if proc.returncode == 0:
            logger.info(f"[FFmpeg] Command succeeded in {elapsed:.2f}s")
            return True, proc.stdout, proc.stderr
        else:
            logger.error(f"[FFmpeg] Command failed (code {proc.returncode}) in {elapsed:.2f}s:\nSTDERR: {proc.stderr[-500:]}")
            return False, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"[FFmpeg] Command timed out after {timeout}s: {cmd_str}")
        return False, "", "Timeout expired"
    except Exception as exc:
        logger.exception(f"[FFmpeg] Unexpected exception executing {cmd_str}: {exc}")
        return False, "", str(exc)


async def run_ffmpeg(cmd: List[str], timeout: int = 120) -> Tuple[bool, str, str]:
    """Asynchronously execute an FFmpeg command in a worker thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _run_ffmpeg_sync, cmd, timeout)


async def extract_audio_mp3(
    src_path: Path,
    dst_path: Path,
    bitrate: str = "192k",
    max_duration: Optional[int] = None,
    timeout: int = 60
) -> bool:
    """
    Extract high quality MP3 audio stream from any media file.
    """
    if not src_path.exists() or src_path.stat().st_size == 0:
        logger.error(f"[FFmpegExtractAudio] Source file missing or empty: {src_path}")
        return False

    cmd = ["ffmpeg", "-y", "-i", str(src_path)]
    if max_duration:
        cmd.extend(["-t", str(max_duration)])
    cmd.extend(["-vn", "-c:a", "libmp3lame", "-b:a", bitrate, str(dst_path)])

    success, _, stderr = await run_ffmpeg(cmd, timeout=timeout)
    if success and dst_path.exists() and dst_path.stat().st_size > 500:
        logger.info(f"[FFmpegExtractAudio] Extracted {dst_path.stat().st_size} bytes to {dst_path.name}")
        return True
    
    logger.error(f"[FFmpegExtractAudio] Failed to extract audio. Output size: {dst_path.stat().st_size if dst_path.exists() else 0}")
    return False


async def apply_audio_filter(
    src_path: Path,
    dst_path: Path,
    audio_filter: str,
    bitrate: str = "192k",
    timeout: int = 60
) -> bool:
    """
    Apply FFmpeg audio filter (e.g. bandpass, vocal suppression) and export as MP3.
    """
    if not src_path.exists() or src_path.stat().st_size == 0:
        logger.error(f"[FFmpegFilter] Source file missing or empty: {src_path}")
        return False

    cmd = [
        "ffmpeg", "-y", "-i", str(src_path),
        "-vn", "-af", audio_filter,
        "-c:a", "libmp3lame", "-b:a", bitrate,
        str(dst_path)
    ]

    success, _, _ = await run_ffmpeg(cmd, timeout=timeout)
    return success and dst_path.exists() and dst_path.stat().st_size > 500


__all__ = ["run_ffmpeg", "extract_audio_mp3", "apply_audio_filter"]
