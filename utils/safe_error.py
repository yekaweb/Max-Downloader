"""
Security utility – safe error messages for end-users.

Never expose raw exception text (stack traces, DB internals, file paths,
tokens) to Telegram users. Use `safe_user_message()` instead.
"""
from __future__ import annotations

import re
from loguru import logger

# Regexes for sensitive patterns we never want users to see
_SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api_key|apikey)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"/[a-zA-Z0-9_./-]{5,}"),          # file paths
    re.compile(r"Traceback \(most recent call last\).*", re.DOTALL),
    re.compile(r"File \".*\", line \d+"),           # stack frame lines
    re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),  # IP addresses
]

# Human-friendly messages for known exception types
_KNOWN_ERRORS: dict[str, str] = {
    "ConnectionRefusedError": "⚠️ خطای اتصال – لطفاً دوباره تلاش کنید.",
    "TimeoutError": "⏰ عملیات دیر شد – لطفاً دوباره تلاش کنید.",
    "asyncio.TimeoutError": "⏰ عملیات دیر شد – لطفاً دوباره تلاش کنید.",
    "DownloadError": "❌ دانلود ناموفق بود – لینک را بررسی کنید.",
    "FileNotFoundError": "❌ فایل موردنظر یافت نشد.",
    "PermissionError": "❌ دسترسی کافی وجود ندارد.",
    "ValueError": "❌ مقدار نامعتبر ارسال شد.",
    "KeyError": "❌ داده‌ای یافت نشد.",
}

_GENERIC_USER_MSG = "❌ خطای داخلی. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."


def safe_user_message(exc: Exception, *, context: str = "") -> str:
    """
    Convert an exception into a safe, user-facing message.

    Logs the full exception internally (with context) but returns only a
    sanitised string suitable for sending to a Telegram user.

    Args:
        exc:     The caught exception.
        context: Optional free-text describing what operation failed
                 (used only in the log, never shown to the user).

    Returns:
        A short, friendly Persian error string.
    """
    exc_type = type(exc).__name__
    raw_msg = str(exc)

    # Log full details internally
    logger.error(
        "[SafeError] {} | context='{}' | exc={}: {}",
        exc_type, context, exc_type, raw_msg,
        exc_info=True
    )

    # Return a friendly mapped message if we recognise the type
    for key, friendly in _KNOWN_ERRORS.items():
        if exc_type == key or key in raw_msg:
            return friendly

    # Fallback: strip anything that looks sensitive, truncate, return generic
    sanitised = raw_msg
    for pattern in _SENSITIVE_PATTERNS:
        sanitised = pattern.sub("[REDACTED]", sanitised)
    sanitised = sanitised.strip()[:80]  # hard cap at 80 chars

    if sanitised and not any(p.search(sanitised) for p in _SENSITIVE_PATTERNS):
        return f"❌ خطا: {sanitised}"

    return _GENERIC_USER_MSG


__all__ = ["safe_user_message"]
