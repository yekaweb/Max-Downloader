"""Shared download session storage for handler modules."""

from typing import Dict, Any

# In-memory per-user session storage for download flow.
# This is temporary and will be replaced by Redis-based FSM state
# once Phase 1 / 1.3 is completed.

download_sessions: Dict[int, Dict[str, Any]] = {}


def get_session(user_id: int) -> Dict[str, Any]:
    """Get or create the current download session data for a user."""
    if user_id not in download_sessions:
        download_sessions[user_id] = {
            "url": None,
            "format_type": None,
            "quality": None,
            "codec": None,
            "subtitle": None,
            "send_as": None,
        }
    return download_sessions[user_id]


def clear_session(user_id: int) -> None:
    """Remove a user session after the download flow completes."""
    if user_id in download_sessions:
        del download_sessions[user_id]
