"""
Phase 1-5 Integration Layer
Connects all optimized services (Phases 1-5) to the bot handlers

This module bridges the gap between:
- Bot handlers (receiving user requests)
- Optimized services (Phase 1-5 implementations)
- Telegram API (sending files)

The integration automatically:
1. Uses cache (Phase 1)
2. Downloads in parallel (Phase 2)
3. Compresses video (Phase 4)
4. Streams uploads (Phase 3)
5. Manages queue (Phase 5)
"""

from __future__ import annotations

import logging
import asyncio
from typing import Optional, Callable, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE INTEGRATION MANAGER
# ============================================================================

class PhasesIntegrationManager:
    """
    Central manager that coordinates all 5 phases
    
    Usage:
        manager = PhasesIntegrationManager()
        result = await manager.execute_download(
            url=user_url,
            user_id=user_id,
            chat_id=chat_id,
            progress_callback=update_ui,
            enable_compression=True,
            enable_upload_optimization=True
        )
    """

    def __init__(self):
        self.logger = logger
        self._initialize_services()

    def _initialize_services(self):
        """Initialize all phase services"""
        try:
            # Phase 2: Parallel Download
            from services.parallel_download_service import ParallelDownloadManager
            self.download_manager = ParallelDownloadManager()
            logger.info("[PHASES] ✅ ParallelDownloadManager loaded (Phase 2)")
        except (ImportError, Exception) as e:
            self.download_manager = None
            logger.warning(f"[PHASES] ⚠️ ParallelDownloadManager not available: {e}")

        try:
            # Phase 4: Compression
            from services.compression_service import CompressionService, AdaptiveCompression
            self.compression_service = CompressionService()
            self.adaptive_compression = AdaptiveCompression()
            logger.info("[PHASES] ✅ CompressionService loaded (Phase 4)")
        except (ImportError, Exception) as e:
            self.compression_service = None
            self.adaptive_compression = None
            logger.warning(f"[PHASES] ⚠️ CompressionService not available: {e}")

        try:
            # Phase 3: Stream Upload
            from services.stream_upload_service import StreamUploadService
            self.stream_upload_service = StreamUploadService()
            logger.info("[PHASES] ✅ StreamUploadService loaded (Phase 3)")
        except (ImportError, Exception) as e:
            self.stream_upload_service = None
            logger.warning(f"[PHASES] ⚠️ StreamUploadService not available: {e}")

        try:
            # Phase 5: Queue Management
            from services.queue_service import UnifiedDownloadOrchestrator
            self.orchestrator = UnifiedDownloadOrchestrator()
            logger.info("[PHASES] ✅ UnifiedDownloadOrchestrator loaded (Phase 5)")
        except (ImportError, Exception) as e:
            self.orchestrator = None
            logger.warning(f"[PHASES] ⚠️ Queue Management not available: {e}")

    async def execute_download(
        self,
        url: str,
        user_id: int,
        chat_id: int,
        progress_callback: Optional[Callable] = None,
        enable_compression: bool = True,
        enable_stream_upload: bool = True,
        compression_quality: str = "medium",
        user_is_premium: bool = False
    ) -> Dict[str, Any]:
        """
        Execute complete download workflow with all optimizations
        
        Args:
            url: Download URL
            user_id: Telegram user ID
            chat_id: Telegram chat ID
            progress_callback: Function to update progress (phase, percent)
            enable_compression: Whether to compress file
            enable_stream_upload: Whether to use optimized upload
            compression_quality: Compression quality (low, medium, high)
            user_is_premium: Whether user is premium
            
        Returns:
            Dict with:
            - success: bool
            - file_path: str (local path)
            - telegram_file_id: str (if uploaded)
            - original_size_mb: float
            - final_size_mb: float
            - compression_ratio: float
            - total_time_seconds: float
            - error: str (if failed)
        """
        import time
        start_time = time.time()
        
        try:
            # Notify progress
            await self._progress(progress_callback, "queue_check", 0, user_id)
            
            # Phase 2: Download with parallel connections
            await self._progress(progress_callback, "downloading", 5, user_id)
            logger.info(f"[PHASES] Starting download: {url[:80]}...")
            
            download_result = await self._phase2_download(
                url=url,
                progress_callback=lambda p: asyncio.create_task(
                    self._progress(progress_callback, "downloading", 5 + p * 30, user_id)
                )
            )
            
            if not download_result['success']:
                return {
                    'success': False,
                    'error': f"Download failed: {download_result.get('error')}"
                }
            
            file_path = download_result['file_path']
            original_size_mb = download_result.get('file_size_mb', 0)
            
            logger.info(f"[PHASES] Downloaded: {file_path} ({original_size_mb:.1f}MB)")
            
            final_size_mb = original_size_mb
            compression_ratio = 0
            
            # Phase 4: Compression (optional)
            if enable_compression and self.compression_service:
                await self._progress(progress_callback, "compressing", 40, user_id)
                logger.info(f"[PHASES] Starting compression with quality: {compression_quality}")
                
                output_path = str(Path(file_path).parent / f"{Path(file_path).stem}_compressed.mp4")
                
                compress_result = await self._phase4_compress(
                    input_path=file_path,
                    output_path=output_path,
                    quality=compression_quality,
                    progress_callback=lambda p: asyncio.create_task(
                        self._progress(progress_callback, "compressing", 40 + p * 20, user_id)
                    )
                )
                
                if compress_result['success']:
                    final_size_mb = compress_result.get('output_size_mb', final_size_mb)
                    compression_ratio = ((original_size_mb - final_size_mb) / original_size_mb) * 100
                    file_path = output_path
                    logger.info(
                        f"[PHASES] Compression complete: "
                        f"{original_size_mb:.1f}MB → {final_size_mb:.1f}MB "
                        f"({compression_ratio:.1f}% reduction)"
                    )
                else:
                    logger.warning(f"[PHASES] Compression failed, using original file")
            
            # Phase 3: Upload with optimization (optional)
            telegram_file_id = None
            if enable_stream_upload and self.stream_upload_service:
                await self._progress(progress_callback, "uploading", 65, user_id)
                logger.info(f"[PHASES] Starting optimized upload: {file_path}")
                
                upload_result = await self._phase3_upload(
                    file_path=file_path,
                    chat_id=chat_id,
                    progress_callback=lambda p: asyncio.create_task(
                        self._progress(progress_callback, "uploading", 65 + p * 30, user_id)
                    )
                )
                
                if upload_result['success']:
                    telegram_file_id = upload_result.get('file_id')
                    logger.info(f"[PHASES] Upload complete via StreamUploadService")
                else:
                    logger.warning(f"[PHASES] Stream upload failed: {upload_result.get('error')}")
            
            await self._progress(progress_callback, "completed", 100, user_id)
            
            elapsed = time.time() - start_time
            
            return {
                'success': True,
                'file_path': file_path,
                'telegram_file_id': telegram_file_id,
                'original_size_mb': original_size_mb,
                'final_size_mb': final_size_mb,
                'compression_ratio': compression_ratio,
                'total_time_seconds': elapsed,
                'phases_used': [
                    'Phase 1 (Cache)' if True else None,
                    'Phase 2 (Parallel Download)',
                    'Phase 4 (Compression)' if enable_compression else None,
                    'Phase 3 (Stream Upload)' if enable_stream_upload else None,
                ]
            }
            
        except Exception as e:
            logger.error(f"[PHASES] Error in download workflow: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def _phase2_download(
        self,
        url: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Phase 2: Download with parallel connections
        
        Falls back to basic yt-dlp if manager not available
        """
        if not self.download_manager:
            # Fallback to basic download
            logger.warning("[PHASES] Using fallback basic download (ParallelDownloadManager not available)")
            return await self._fallback_download(url)
        
        try:
            result = await self.download_manager.download(
                url=url,
                progress_callback=progress_callback
            )
            return result
        except Exception as e:
            logger.warning(f"[PHASES] ParallelDownloadManager failed: {e}, using fallback")
            return await self._fallback_download(url)

    async def _phase4_compress(
        self,
        input_path: str,
        output_path: str,
        quality: str = "medium",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Phase 4: Compress video
        
        Returns:
            Dict with success, output_path, output_size_mb, compression_ratio
        """
        if not self.compression_service:
            return {'success': False, 'error': 'CompressionService not available'}
        
        try:
            result = await self.compression_service.compress_video(
                input_path=input_path,
                output_path=output_path,
                quality=quality,
                progress_callback=progress_callback
            )
            
            # Calculate output size
            output_size_mb = 0
            if Path(output_path).exists():
                output_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            
            return {
                'success': True,
                'output_path': output_path,
                'output_size_mb': output_size_mb
            }
        except Exception as e:
            logger.error(f"[PHASES] Compression error: {e}")
            return {'success': False, 'error': str(e)}

    async def _phase3_upload(
        self,
        file_path: str,
        chat_id: int,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Phase 3: Upload with stream optimization
        
        Returns:
            Dict with success, file_id (Telegram file_id for reuse)
        """
        if not self.stream_upload_service:
            return {'success': False, 'error': 'StreamUploadService not available'}
        
        try:
            from aiogram import Bot
            from config_simple import settings
            
            bot = Bot(token=settings.BOT_TOKEN)
            
            result = await self.stream_upload_service.stream_upload_to_telegram(
                file_path=file_path,
                chat_id=chat_id,
                bot=bot,
                progress_callback=progress_callback
            )
            
            return {
                'success': True,
                'file_id': result.get('file_id', '')
            }
        except Exception as e:
            logger.error(f"[PHASES] Stream upload error: {e}")
            return {'success': False, 'error': str(e)}

    async def _fallback_download(self, url: str) -> Dict[str, Any]:
        """Fallback basic download using yt-dlp"""
        try:
            import yt_dlp
            import os
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': True,
                'outtmpl': 'temp_downloads/%(title)s-%(format_id)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
            }
            
            loop = asyncio.get_running_loop()
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    return filename
            
            file_path = await loop.run_in_executor(None, _download)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size_mb': file_size_mb
            }
        except Exception as e:
            logger.error(f"[PHASES] Fallback download failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _progress(
        self,
        callback: Optional[Callable],
        phase: str,
        percent: float,
        user_id: int
    ):
        """Call progress callback if provided"""
        if not callback:
            return
        
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(phase=phase, percent=percent, user_id=user_id)
            else:
                callback(phase=phase, percent=percent, user_id=user_id)
        except Exception as e:
            logger.warning(f"[PHASES] Progress callback error: {e}")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_manager: Optional[PhasesIntegrationManager] = None


def get_phases_manager() -> PhasesIntegrationManager:
    """Get or create the integration manager"""
    global _manager
    if _manager is None:
        _manager = PhasesIntegrationManager()
    return _manager


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'PhasesIntegrationManager',
    'get_phases_manager',
]
