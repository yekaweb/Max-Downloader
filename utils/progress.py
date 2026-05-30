"""Progress bar generator - Beautiful visual progress updates with emoji and stats"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio


# Global progress message throttle locks (per user_id)
_progress_locks: Dict[int, asyncio.Lock] = {}
_throttle_times: Dict[int, float] = {}


def get_progress_lock(user_id: int) -> asyncio.Lock:
    """Get or create an asyncio.Lock for throttling progress messages per user"""
    if user_id not in _progress_locks:
        _progress_locks[user_id] = asyncio.Lock()
    return _progress_locks[user_id]


class ProgressBar:
    """Generate beautiful progress bar updates for downloads"""

    # Emoji bars for different styles
    BARS = {
        "gradient": ["▰", "▱"],  # Filled and empty
        "block": ["█", "░"],  # Block style
        "circle": ["⬤", "○"],  # Circle style
        "square": ["■", "□"],  # Square style
        "arrow": ["➤", "─"],  # Arrow style
    }

    # Speed and time emojis
    EMOJI_ICONS = {
        "speed": "⚡",
        "eta": "⏱",
        "progress": "📊",
        "download": "📥",
        "upload": "📤",
        "check": "✅",
        "error": "❌",
    }

    def __init__(self, bar_style: str = "gradient", bar_length: int = 20):
        """
        Initialize progress bar generator

        Args:
            bar_style: Style of bar - 'gradient', 'block', 'circle', 'square', 'arrow'
            bar_length: Length of progress bar (default 20)
        """
        self.bar_style = bar_style
        self.bar_length = bar_length
        self.bar_chars = self.BARS.get(bar_style, self.BARS["gradient"])

    def generate(
        self,
        current: int,
        total: int,
        speed: Optional[float] = None,
        eta_seconds: Optional[int] = None,
        title: Optional[str] = None,
        show_percent: bool = True,
        show_bytes: bool = True,
    ) -> str:
        """
        Generate a single progress bar line with stats.

        Args:
            current: Current bytes downloaded
            total: Total bytes to download
            speed: Download speed in bytes/sec (optional)
            eta_seconds: Estimated time remaining in seconds (optional)
            title: Title for the progress bar (optional)
            show_percent: Show percentage (default True)
            show_bytes: Show bytes (default True)

        Returns:
            Formatted progress bar string
        """
        if total <= 0:
            return "Invalid progress data"

        # Calculate percentage
        percent = (current / total) * 100
        percent = min(100, max(0, percent))  # Clamp 0-100

        # Calculate filled portion
        filled = int((percent / 100) * self.bar_length)

        # Build bar
        bar = (
            self.bar_chars[0] * filled
            + self.bar_chars[1] * (self.bar_length - filled)
        )

        # Build output
        lines = []

        # Title if provided
        if title:
            lines.append(f"{self.EMOJI_ICONS['download']} {title}")

        # Progress bar with percentage
        if show_percent:
            percent_str = f"{percent:.1f}%"
            lines.append(f"[{bar}] {percent_str}")
        else:
            lines.append(f"[{bar}]")

        # Bytes and stats
        stats = []
        if show_bytes:
            current_mb = self._format_bytes(current)
            total_mb = self._format_bytes(total)
            stats.append(f"{current_mb}/{total_mb}")

        if speed is not None:
            speed_str = self._format_speed(speed)
            stats.append(f"{self.EMOJI_ICONS['speed']} {speed_str}")

        if eta_seconds is not None:
            eta_str = self._format_eta(eta_seconds)
            stats.append(f"{self.EMOJI_ICONS['eta']} {eta_str}")

        if stats:
            lines.append(" | ".join(stats))

        return "\n".join(lines)

    def generate_compact(
        self,
        current: int,
        total: int,
        speed: Optional[float] = None,
        eta_seconds: Optional[int] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Generate a single-line compact progress bar.

        Args:
            current: Current bytes downloaded
            total: Total bytes to download
            speed: Download speed in bytes/sec (optional)
            eta_seconds: Estimated time remaining in seconds (optional)
            title: Title prefix (optional)

        Returns:
            Single line formatted progress string
        """
        if total <= 0:
            return "Invalid progress data"

        percent = (current / total) * 100
        percent = min(100, max(0, percent))

        filled = int((percent / 100) * self.bar_length)
        bar = (
            self.bar_chars[0] * filled
            + self.bar_chars[1] * (self.bar_length - filled)
        )

        # Compact format
        result = ""

        if title:
            result = f"{title} "

        result += f"[{bar}] {percent:.1f}%"

        if speed is not None:
            result += f" @ {self._format_speed(speed)}"

        if eta_seconds is not None:
            result += f" ETA: {self._format_eta(eta_seconds)}"

        return result

    def generate_detailed(
        self,
        current: int,
        total: int,
        speed: Optional[float] = None,
        eta_seconds: Optional[int] = None,
        elapsed_seconds: Optional[int] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Generate detailed multi-line progress with all information.

        Args:
            current: Current bytes downloaded
            total: Total bytes to download
            speed: Download speed in bytes/sec (optional)
            eta_seconds: Estimated time remaining in seconds (optional)
            elapsed_seconds: Time elapsed in seconds (optional)
            title: Title for the download (optional)

        Returns:
            Formatted detailed progress string
        """
        if total <= 0:
            return "Invalid progress data"

        lines = []

        # Header
        if title:
            lines.append(f"{self.EMOJI_ICONS['download']} **{title}**")
            lines.append("=" * 50)

        # Progress bar
        percent = (current / total) * 100
        percent = min(100, max(0, percent))

        filled = int((percent / 100) * self.bar_length)
        bar = (
            self.bar_chars[0] * filled
            + self.bar_chars[1] * (self.bar_length - filled)
        )

        lines.append(f"Progress: [{bar}] {percent:.1f}%")

        # Detailed stats
        current_mb = self._format_bytes(current)
        total_mb = self._format_bytes(total)
        lines.append(f"Downloaded: {current_mb} / {total_mb}")

        if speed is not None:
            speed_str = self._format_speed(speed)
            lines.append(f"{self.EMOJI_ICONS['speed']} Speed: {speed_str}")

        if elapsed_seconds is not None:
            elapsed_str = self._format_eta(elapsed_seconds)
            lines.append(f"⏱ Elapsed: {elapsed_str}")

        if eta_seconds is not None:
            eta_str = self._format_eta(eta_seconds)
            lines.append(f"{self.EMOJI_ICONS['eta']} ETA: {eta_str}")

        return "\n".join(lines)

    @staticmethod
    def _format_bytes(bytes_size: int) -> str:
        """Format bytes to human-readable string"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"

    @staticmethod
    def _format_speed(bytes_per_sec: float) -> str:
        """Format download speed"""
        if bytes_per_sec is None or bytes_per_sec == 0:
            return "0 B/s"

        for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
            if bytes_per_sec < 1024:
                return f"{bytes_per_sec:.1f}{unit}"
            bytes_per_sec /= 1024
        return f"{bytes_per_sec:.1f}TB/s"

    @staticmethod
    def _format_eta(seconds: int) -> str:
        """Format ETA to human-readable string"""
        if seconds is None or seconds < 0:
            return "Unknown"

        if seconds < 60:
            return f"{seconds}s"

        minutes = seconds // 60
        secs = seconds % 60

        if minutes < 60:
            return f"{minutes}m {secs}s"

        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"


# Shorthand functions for quick usage
def create_progress_bar(
    current: int,
    total: int,
    speed: Optional[float] = None,
    eta: Optional[int] = None,
    title: Optional[str] = None,
) -> str:
    """Create a standard progress bar"""
    pb = ProgressBar(bar_style="gradient", bar_length=20)
    return pb.generate(current, total, speed, eta, title)


def create_compact_progress_bar(
    current: int,
    total: int,
    speed: Optional[float] = None,
    eta: Optional[int] = None,
    title: Optional[str] = None,
) -> str:
    """Create a single-line compact progress bar"""
    pb = ProgressBar(bar_style="block", bar_length=15)
    return pb.generate_compact(current, total, speed, eta, title)


def create_detailed_progress_bar(
    current: int,
    total: int,
    speed: Optional[float] = None,
    eta: Optional[int] = None,
    elapsed: Optional[int] = None,
    title: Optional[str] = None,
) -> str:
    """Create a detailed multi-line progress bar"""
    pb = ProgressBar(bar_style="gradient", bar_length=25)
    return pb.generate_detailed(current, total, speed, eta, elapsed, title)


def generate_progress_message(
    title: str,
    progress_percent: float,
    downloaded_mb: float,
    total_mb: float,
    speed_mbps: float,
    eta_seconds: int,
    queue_position: int = 0,
    phase: str = "download",  # "download", "upload", "processing"
    use_html: bool = True,
) -> str:
    """
    Generate a beautiful progress message for Telegram with dynamic phase icons.
    
    Args:
        title: Download title (video/audio name)
        progress_percent: Progress percentage (0-100)
        downloaded_mb: Downloaded size in MB
        total_mb: Total size in MB
        speed_mbps: Download speed in MB/s
        eta_seconds: Estimated time remaining in seconds
        queue_position: Position in download queue (0 if not queued)
        phase: Current phase - "download", "upload", or "processing"
        use_html: Use HTML formatting for Telegram (default True)
    
    Returns:
        Formatted progress message string
    """
    # Clamp progress to 0-100
    progress_percent = min(100, max(0, progress_percent))
    
    # Phase configuration
    phase_icons = {
        "download": "⬇️",
        "upload": "⬆️",
        "processing": "⚙️",
    }
    
    phase_labels = {
        "download": "در حال دانلود",
        "upload": "در حال ارسال به تلگرام",
        "processing": "در حال پردازش",
    }
    
    # Default to "download" if phase not recognized
    phase_icon = phase_icons.get(phase, phase_icons["download"])
    phase_label = phase_labels.get(phase, phase_labels["download"])
    
    # Progress bar visualization
    bar_length = 20
    filled = int(bar_length * progress_percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Format ETA
    eta_str = _format_eta_string(eta_seconds)
    
    # Truncate title to prevent message overflow
    title_display = title[:45] + "..." if len(title) > 45 else title
    
    if use_html:
        # HTML formatted for Telegram
        message = f"""
{phase_icon} <b>{phase_label}</b>

🎬 <code>{title_display}</code>

[{bar}] {progress_percent:.1f}%

📦 حجم: {downloaded_mb:.1f} / {total_mb:.1f} MB
⚡ سرعت: {speed_mbps:.2f} MB/s
⏱ زمان باقی‌مانده: {eta_str}"""
    else:
        # Plain text format
        message = f"""
{phase_icon} {phase_label}

🎬 {title_display}

[{bar}] {progress_percent:.1f}%

📦 حجم: {downloaded_mb:.1f} / {total_mb:.1f} MB
⚡ سرعت: {speed_mbps:.2f} MB/s
⏱ زمان باقی‌مانده: {eta_str}"""
    
    # Add queue position if provided
    if queue_position > 0:
        if use_html:
            message += f"\n\n📋 موقعیت در صف: <b>{queue_position}</b>"
        else:
            message += f"\n\n📋 موقعیت در صف: {queue_position}"
    
    # Add waiting notice
    if use_html:
        message += "\n\n<i>⚠️ لطفاً صبر کنید، ربات در حال کار است...</i>"
    else:
        message += "\n\n⚠️ لطفاً صبر کنید، ربات در حال کار است..."
    
    return message.strip()


async def can_update_progress(user_id: int, throttle_seconds: float = 3.0) -> bool:
    """
    Check if enough time has passed to update progress (throttle control).
    Returns True if update is allowed, False if still within throttle window.
    
    Uses asyncio.Lock to prevent concurrent updates.
    Max 1 update per `throttle_seconds` (default 3 seconds).
    
    Args:
        user_id: Telegram user ID
        throttle_seconds: Minimum seconds between updates (default 3.0)
    
    Returns:
        True if update is allowed, False if still throttled
    """
    current_time = datetime.now().timestamp()
    last_update = _throttle_times.get(user_id, 0)
    
    # Check if enough time has passed
    if current_time - last_update >= throttle_seconds:
        _throttle_times[user_id] = current_time
        return True
    
    return False


async def update_progress_message(
    message,
    user_id: int,
    chat_id: int,
    message_id: int,
    title: str,
    progress_percent: float,
    downloaded_mb: float,
    total_mb: float,
    speed_mbps: float,
    eta_seconds: int,
    queue_position: int = 0,
    phase: str = "download",
    throttle_seconds: float = 3.0,
) -> bool:
    """
    Update a Telegram progress message with proper throttling to prevent rate limits.
    
    Uses asyncio.Lock to ensure only one update is in flight at a time.
    Throttles updates to max 1 per `throttle_seconds` (default 3 seconds).
    
    Args:
        message: aiogram Message object (bot instance)
        user_id: Telegram user ID (for throttle key)
        chat_id: Telegram chat ID
        message_id: Message ID to edit
        title: Download title
        progress_percent: Progress percentage (0-100)
        downloaded_mb: Downloaded size in MB
        total_mb: Total size in MB
        speed_mbps: Download speed in MB/s
        eta_seconds: Estimated time remaining
        queue_position: Position in queue (optional)
        phase: Current phase ("download", "upload", "processing")
        throttle_seconds: Seconds between updates (default 3.0)
    
    Returns:
        True if message was updated, False if throttled
    """
    # Get user's progress lock
    lock = get_progress_lock(user_id)
    
    # Check throttle first to avoid unnecessary lock acquisition
    if not await can_update_progress(user_id, throttle_seconds):
        return False
    
    # Acquire lock to prevent concurrent edits
    async with lock:
        # Double-check throttle inside lock (in case another task just updated)
        if not await can_update_progress(user_id, throttle_seconds):
            return False
        
        try:
            # Generate the progress message
            progress_msg = generate_progress_message(
                title=title,
                progress_percent=progress_percent,
                downloaded_mb=downloaded_mb,
                total_mb=total_mb,
                speed_mbps=speed_mbps,
                eta_seconds=eta_seconds,
                queue_position=queue_position,
                phase=phase,
                use_html=True,
            )
            
            # Edit the message in Telegram
            await message.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=progress_msg,
                parse_mode="HTML",
            )
            
            return True
        except Exception as e:
            # Silently fail on edit errors (message deleted, etc.)
            from loguru import logger
            logger.debug(f"Failed to update progress message: {e}")
            return False


def _format_eta_string(seconds: int) -> str:
    """Format ETA in seconds to human-readable Persian string"""
    if seconds is None or seconds < 0:
        return "نامشخص"
    
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    secs = seconds % 60
    
    if minutes < 60:
        if secs == 0:
            return f"{minutes}m"
        return f"{minutes}m {secs}s"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


__all__ = [
    "ProgressBar",
    "create_progress_bar",
    "create_compact_progress_bar",
    "create_detailed_progress_bar",
    "generate_progress_message",
    "update_progress_message",
    "can_update_progress",
    "get_progress_lock",
]
