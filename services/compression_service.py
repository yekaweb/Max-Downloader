"""
PHASE 4: Compression Service + بهینه‌سازی فایل
مرحله 4.1, 4.2, 4.3 - فشرده‌سازی هوشمند
"""

from __future__ import annotations

import asyncio
import subprocess
import logging
import os
from typing import Dict, Optional, Callable, List, Union
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

# ============================================
# Quality Presets
# ============================================

class VideoQuality(str, Enum):
    """کیفیت ویدیو"""
    ULTRA_LOW = "ultra_low"      # 480p, 500kbps (20% اندازه اصلی)
    LOW = "low"                    # 720p, 1000kbps (30%)
    MEDIUM = "medium"              # 1080p, 2000kbps (50%)
    HIGH = "high"                  # 1440p, 4000kbps (70%)
    ULTRA_HIGH = "ultra_high"     # 2160p, 8000kbps (90%)


class AudioQuality(str, Enum):
    """کیفیت صوت"""
    ULTRA_LOW = "ultra_low"    # 32kbps (mono)
    LOW = "low"                  # 64kbps (mono)
    MEDIUM = "medium"            # 128kbps (stereo)
    HIGH = "high"                # 192kbps (stereo)
    ULTRA_HIGH = "ultra_high"   # 320kbps (stereo)


class CompressionPreset(str, Enum):
    """سرعت و کیفیت فشرده‌سازی"""
    ULTRAFAST = "ultrafast"    # سریع‌ترین (بدترین کیفیت)
    SUPERFAST = "superfast"
    VERYFAST = "veryfast"
    FASTER = "faster"
    FAST = "fast"               # تعادل (Default)
    MEDIUM = "medium"
    SLOW = "slow"
    SLOWER = "slower"
    VERYSLOW = "veryslow"       # کندترین (بهترین کیفیت)


# ============================================
# مرحله 4.1: CompressionService
# ============================================

class CompressionService:
    """
    فشرده‌سازی فایل‌ها با FFmpeg
    
    Features:
    - Video compression (H.264/H.265)
    - Audio compression (AAC/Opus)
    - Image compression (JPEG/WebP)
    - Quality presets (5 level)
    - Codec selection
    - Bitrate optimization
    - Progress tracking
    """
    
    # Video codec options
    VIDEO_PRESETS = {
        VideoQuality.ULTRA_LOW: {
            'codec': 'libx264',
            'crf': 35,  # 0-51, lower = better
            'bitrate': '500k',
            'preset': CompressionPreset.FAST,
            'resolution': '480'
        },
        VideoQuality.LOW: {
            'codec': 'libx264',
            'crf': 30,
            'bitrate': '1000k',
            'preset': CompressionPreset.FAST,
            'resolution': '720'
        },
        VideoQuality.MEDIUM: {
            'codec': 'libx264',
            'crf': 23,
            'bitrate': '2000k',
            'preset': CompressionPreset.MEDIUM,
            'resolution': '1080'
        },
        VideoQuality.HIGH: {
            'codec': 'libx264',
            'crf': 18,
            'bitrate': '4000k',
            'preset': CompressionPreset.MEDIUM,
            'resolution': '1440'
        },
        VideoQuality.ULTRA_HIGH: {
            'codec': 'libx265',  # H.265 for better compression
            'crf': 22,
            'bitrate': '8000k',
            'preset': CompressionPreset.SLOW,
            'resolution': '2160'
        }
    }
    
    # Audio codec options
    AUDIO_PRESETS = {
        AudioQuality.ULTRA_LOW: {
            'codec': 'aac',
            'bitrate': '32k',
            'channels': 1  # mono
        },
        AudioQuality.LOW: {
            'codec': 'aac',
            'bitrate': '64k',
            'channels': 1
        },
        AudioQuality.MEDIUM: {
            'codec': 'aac',
            'bitrate': '128k',
            'channels': 2  # stereo
        },
        AudioQuality.HIGH: {
            'codec': 'libopus',
            'bitrate': '192k',
            'channels': 2
        },
        AudioQuality.ULTRA_HIGH: {
            'codec': 'libopus',
            'bitrate': '320k',
            'channels': 2
        }
    }
    
    def __init__(self):
        """Initialize CompressionService"""
        self.active_compressions = {}  # {file_path: {status, progress}}
        self.lock = asyncio.Lock()
        logger.info("[COMPRESS] CompressionService initialized")
    
    async def compress_video(
        self,
        input_path: str,
        output_path: str,
        quality: Union[str, VideoQuality] = VideoQuality.MEDIUM,
        audio_quality: Union[str, AudioQuality] = AudioQuality.MEDIUM,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        فشرده‌سازی ویدیو
        
        Args:
            input_path: مسیر فایل اصلی
            output_path: مسیر فایل خروجی
            quality: کیفیت ویدیو یا نام کیفیت
            audio_quality: کیفیت صوت یا نام کیفیت
            progress_callback: Callback for progress
        
        Returns:
            {'status': 'success/failed', 'compression_ratio': float, ...}
        """
        logger.info(f"[COMPRESS-V] Starting video compression: {input_path}")
        
        if isinstance(quality, str):
            try:
                quality = VideoQuality(quality)
            except ValueError:
                quality = VideoQuality.MEDIUM
        if isinstance(audio_quality, str):
            try:
                audio_quality = AudioQuality(audio_quality)
            except ValueError:
                audio_quality = AudioQuality.MEDIUM
        
        file_id = input_path
        start_time = datetime.utcnow()
        
        try:
            # ثبت در active
            async with self.lock:
                self.active_compressions[file_id] = {
                    'type': 'video',
                    'status': 'compressing',
                    'progress': 0,
                    'input': input_path,
                    'output': output_path,
                    'quality': quality.value,
                    'start_time': start_time
                }
            
            # گرفتن preset
            video_preset = self.VIDEO_PRESETS[quality]
            audio_preset = self.AUDIO_PRESETS[audio_quality]
            
            # ایجاد FFmpeg command
            cmd = self._build_ffmpeg_command(
                input_path,
                output_path,
                video_preset,
                audio_preset
            )
            
            logger.info(f"[COMPRESS-V] FFmpeg command: {' '.join(cmd)}")
            
            # اجرای FFmpeg
            result = await self._run_ffmpeg(
                cmd,
                file_id,
                progress_callback
            )
            
            if result['status'] != 'success':
                return result
            
            # محاسبه compression ratio
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            compression_ratio = (1 - output_size / input_size) * 100
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"[COMPRESS-V] ✅ Compression completed\n"
                f"             Input: {input_size/(1024*1024):.1f}MB\n"
                f"             Output: {output_size/(1024*1024):.1f}MB\n"
                f"             Ratio: {compression_ratio:.1f}%\n"
                f"             Time: {duration:.1f}s"
            )
            
            return {
                'status': 'success',
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': compression_ratio,
                'duration': duration,
                'quality': quality.value
            }
        
        except Exception as e:
            logger.error(f"[COMPRESS-V] ❌ Error: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'input': input_path
            }
        
        finally:
            async with self.lock:
                if file_id in self.active_compressions:
                    del self.active_compressions[file_id]
    
    async def compress_audio(
        self,
        input_path: str,
        output_path: str,
        quality: Union[str, AudioQuality] = AudioQuality.MEDIUM,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        فشرده‌سازی صوت
        
        Args:
            input_path: مسیر فایل صوت
            output_path: مسیر خروجی
            quality: کیفیت صوت یا نام کیفیت
            progress_callback: Progress callback
        
        Returns:
            Compression result dict
        """
        logger.info(f"[COMPRESS-A] Starting audio compression: {input_path}")
        
        if isinstance(quality, str):
            try:
                quality = AudioQuality(quality)
            except ValueError:
                quality = AudioQuality.MEDIUM
        
        file_id = input_path
        start_time = datetime.utcnow()
        
        try:
            async with self.lock:
                self.active_compressions[file_id] = {
                    'type': 'audio',
                    'status': 'compressing',
                    'progress': 0,
                    'quality': quality.value,
                    'start_time': start_time
                }
            
            preset = self.AUDIO_PRESETS[quality]
            
            # Build FFmpeg command for audio
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:a', preset['codec'],
                '-b:a', preset['bitrate'],
                '-ac', str(preset['channels']),
                '-q:a', '4',  # VBR quality
                '-y',
                output_path
            ]
            
            result = await self._run_ffmpeg(cmd, file_id, progress_callback)
            
            if result['status'] == 'success':
                input_size = os.path.getsize(input_path)
                output_size = os.path.getsize(output_path)
                compression_ratio = (1 - output_size / input_size) * 100
                
                logger.info(f"[COMPRESS-A] ✅ Audio compressed: {compression_ratio:.1f}%")
                
                return {
                    'status': 'success',
                    'input_size': input_size,
                    'output_size': output_size,
                    'compression_ratio': compression_ratio,
                    'quality': quality.value
                }
            
            return result
        
        except Exception as e:
            logger.error(f"[COMPRESS-A] ❌ Error: {e}")
            return {'status': 'failed', 'error': str(e)}
        
        finally:
            async with self.lock:
                if file_id in self.active_compressions:
                    del self.active_compressions[file_id]
    
    def _build_ffmpeg_command(
        self,
        input_path: str,
        output_path: str,
        video_preset: Dict,
        audio_preset: Dict
    ) -> List[str]:
        """ایجاد FFmpeg command"""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            # Video encoding
            '-c:v', video_preset['codec'],
            '-crf', str(video_preset['crf']),
            '-preset', video_preset['preset'].value,
            '-b:v', video_preset['bitrate'],
            '-vf', f"scale=-1:{video_preset['resolution']}",
            # Audio encoding
            '-c:a', audio_preset['codec'],
            '-b:a', audio_preset['bitrate'],
            '-ac', str(audio_preset['channels']),
            # Other options
            '-movflags', 'faststart',  # For streaming
            '-y',  # Overwrite output
            output_path
        ]
        
        return cmd
    
    async def _run_ffmpeg(
        self,
        cmd: List[str],
        file_id: str,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """اجرای FFmpeg process"""
        try:
            logger.info(f"[COMPRESS] Running FFmpeg: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode('utf-8', errors='replace').strip() if stdout else ''
            stderr_text = stderr.decode('utf-8', errors='replace').strip() if stderr else ''
            
            if process.returncode == 0:
                if stdout_text:
                    logger.debug(f"[COMPRESS] FFmpeg stdout: {stdout_text}")
                if stderr_text:
                    logger.debug(f"[COMPRESS] FFmpeg stderr: {stderr_text}")
                logger.info(f"[COMPRESS] FFmpeg succeeded")
                return {'status': 'success'}
            else:
                error_msg = stderr_text or stdout_text or f"FFmpeg failed with return code {process.returncode}"
                logger.error(f"[COMPRESS] FFmpeg failed: {error_msg}")
                return {'status': 'failed', 'error': error_msg}
        
        except Exception as e:
            logger.exception(f"[COMPRESS] Subprocess error while running FFmpeg")
            return {'status': 'failed', 'error': f"{type(e).__name__}: {e}"}
    
    async def get_compression_status(self, file_id: str) -> Optional[Dict]:
        """وضعیت فشرده‌سازی فایل"""
        async with self.lock:
            return self.active_compressions.get(file_id)
    
    async def get_all_compressions(self) -> Dict:
        """تمام فشرده‌سازی‌های فعال"""
        async with self.lock:
            return dict(self.active_compressions)


# ============================================
# مرحله 4.2: AdaptiveCompression
# ============================================

class AdaptiveCompression:
    """
    انتخاب خودکار کیفیت براساس:
    - اندازه فایل
    - نوع فایل
    - دستگاه کاربر
    - سرعت اینترنت
    """
    
    def __init__(self):
        self.service = CompressionService()
        logger.info("[ADAPTIVE] AdaptiveCompression initialized")
    
    async def auto_compress(
        self,
        file_path: str,
        output_path: str,
        target_size_mb: Optional[int] = None,
        device_type: str = "mobile",  # mobile, tablet, desktop
        connection: str = "4g",  # 2g, 3g, 4g, 5g, wifi
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        فشرده‌سازی خودکار براساس شرایط
        
        Args:
            file_path: مسیر فایل
            output_path: مسیر خروجی
            target_size_mb: اندازه هدف (اختیاری)
            device_type: نوع دستگاه
            connection: نوع اتصال
            progress_callback: Progress callback
        
        Returns:
            Compression result
        """
        logger.info(f"[ADAPTIVE] Auto-compressing: {file_path}")
        
        # تعیین کیفیت براساس شرایط
        quality = self._determine_quality(
            file_path,
            target_size_mb,
            device_type,
            connection
        )
        
        logger.info(
            f"[ADAPTIVE] Selected quality: {quality.value}\n"
            f"           Device: {device_type}, Connection: {connection}"
        )
        
        # فشرده‌سازی
        result = await self.service.compress_video(
            file_path,
            output_path,
            quality=quality,
            progress_callback=progress_callback
        )
        
        return result
    
    def _determine_quality(
        self,
        file_path: str,
        target_size_mb: Optional[int],
        device_type: str,
        connection: str
    ) -> VideoQuality:
        """
        تعیین کیفیت براساس شرایط
        
        Algorithm:
        1. از اندازه فایل شروع کنید
        2. براساس دستگاه تنظیم کنید
        3. براساس اتصال تنظیم کنید
        4. اگر target_size تنظیم کنید
        """
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # تعیین ابتدایی براساس اندازه
        if file_size_mb < 10:
            quality = VideoQuality.MEDIUM
        elif file_size_mb < 50:
            quality = VideoQuality.MEDIUM
        elif file_size_mb < 100:
            quality = VideoQuality.LOW
        elif file_size_mb < 500:
            quality = VideoQuality.ULTRA_LOW
        else:
            quality = VideoQuality.ULTRA_LOW
        
        # تنظیم براساس دستگاه
        if device_type == "mobile":
            # موبایل نیاز کمتری دارد
            if quality == VideoQuality.ULTRA_HIGH:
                quality = VideoQuality.HIGH
            elif quality == VideoQuality.HIGH:
                quality = VideoQuality.MEDIUM
        elif device_type == "desktop":
            # دسکتاپ می‌تواند کیفیت بیشتر را پشتیبانی کند
            if quality == VideoQuality.ULTRA_LOW:
                quality = VideoQuality.LOW
            elif quality == VideoQuality.LOW:
                quality = VideoQuality.MEDIUM
        
        # تنظیم براساس اتصال
        if connection in ["2g", "3g"]:
            quality = VideoQuality.ULTRA_LOW
        elif connection == "4g":
            if quality == VideoQuality.ULTRA_HIGH:
                quality = VideoQuality.HIGH
        elif connection in ["5g", "wifi"]:
            pass  # بدون تغییر
        
        # اگر target_size داشتیم، کاهش بیشتری
        if target_size_mb and file_size_mb / target_size_mb > 5:
            quality = VideoQuality.ULTRA_LOW
        
        return quality
    
    async def get_estimated_size(
        self,
        file_path: str,
        quality: VideoQuality = VideoQuality.MEDIUM
    ) -> Dict:
        """
        تخمین اندازه خروجی (بدون فشرده‌سازی)
        
        Returns:
            {'estimated_mb': float, 'compression_percent': float}
        """
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        
        # تخمین براساس preset
        preset = CompressionService.VIDEO_PRESETS[quality]
        
        # Bitrate in Mbps
        bitrate = int(preset['bitrate'].replace('k', '')) / 1000
        
        # درخواست FFmpeg برای مدت زمان
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1:nokey=1',
            file_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            duration = float(stdout.decode().strip())
            
            # Calculate estimated size
            estimated_size_mb = (bitrate * duration) / 60 / 8
            compression_percent = (1 - estimated_size_mb / file_size) * 100
            
            return {
                'original_mb': file_size,
                'estimated_mb': estimated_size_mb,
                'compression_percent': compression_percent,
                'estimated_time_sec': duration / 2  # Rough estimate
            }
        
        except Exception as e:
            logger.error(f"[ADAPTIVE] Error estimating size: {e}")
            return {
                'error': str(e),
                'original_mb': file_size
            }


# ============================================
# مرحله 4.3: FormatOptimization
# ============================================

class FormatOptimization:
    """
    بهینه‌سازی فرمت برای پلتفرم‌های مختلف
    """
    
    PLATFORM_PRESETS = {
        'telegram': {
            'max_size_mb': 2000,
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'container': 'mp4',
            'quality': VideoQuality.MEDIUM
        },
        'whatsapp': {
            'max_size_mb': 16,
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'container': 'mp4',
            'quality': VideoQuality.LOW
        },
        'instagram': {
            'max_size_mb': 100,
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'container': 'mp4',
            'quality': VideoQuality.MEDIUM,
            'aspect_ratio': '9:16'  # Story
        },
        'youtube': {
            'max_size_mb': 256000,
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'container': 'mp4',
            'quality': VideoQuality.HIGH
        },
        'twitter': {
            'max_size_mb': 512,
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'container': 'mp4',
            'quality': VideoQuality.MEDIUM
        }
    }
    
    def __init__(self):
        self.compression = AdaptiveCompression()
        logger.info("[FORMAT] FormatOptimization initialized")
    
    async def optimize_for_platform(
        self,
        file_path: str,
        output_path: str,
        platform: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        بهینه‌سازی برای پلتفرم خاص
        
        Args:
            file_path: فایل اصلی
            output_path: فایل خروجی
            platform: پلتفرم (telegram, whatsapp, etc)
            progress_callback: Progress callback
        
        Returns:
            Optimization result
        """
        logger.info(f"[FORMAT] Optimizing for {platform}: {file_path}")
        
        if platform not in self.PLATFORM_PRESETS:
            return {
                'status': 'failed',
                'error': f'Platform {platform} not supported'
            }
        
        preset = self.PLATFORM_PRESETS[platform]
        
        # دانلود خودکار براساس preset
        result = await self.compression.auto_compress(
            file_path,
            output_path,
            target_size_mb=preset['max_size_mb'],
            progress_callback=progress_callback
        )
        
        return result
    
    def get_supported_platforms(self) -> List[str]:
        """لیست پلتفرم‌های پشتیبانی‌شده"""
        return list(self.PLATFORM_PRESETS.keys())


# ============================================
# Global Instances
# ============================================

_global_compression: Optional[CompressionService] = None
_global_adaptive: Optional[AdaptiveCompression] = None
_global_format: Optional[FormatOptimization] = None


async def get_compression_service() -> CompressionService:
    """گرفتن global CompressionService instance"""
    global _global_compression
    if _global_compression is None:
        _global_compression = CompressionService()
    return _global_compression


async def get_adaptive_compression() -> AdaptiveCompression:
    """گرفتن global AdaptiveCompression instance"""
    global _global_adaptive
    if _global_adaptive is None:
        _global_adaptive = AdaptiveCompression()
    return _global_adaptive


async def get_format_optimization() -> FormatOptimization:
    """گرفتن global FormatOptimization instance"""
    global _global_format
    if _global_format is None:
        _global_format = FormatOptimization()
    return _global_format


__all__ = [
    'CompressionService',
    'AdaptiveCompression',
    'FormatOptimization',
    'VideoQuality',
    'AudioQuality',
    'CompressionPreset',
    'get_compression_service',
    'get_adaptive_compression',
    'get_format_optimization'
]
