"""Utilities - formatters and helpers"""


def format_file_size(bytes_size: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def format_duration(seconds: int) -> str:
    """Format seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


__all__ = ["format_file_size", "format_duration"]
