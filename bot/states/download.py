"""FSM states for download flow with explicit video/audio branching"""
from aiogram.fsm.state import StatesGroup, State


class DownloadStates(StatesGroup):
    """
    Finite State Machine for download workflow.
    
    Explicit branching into video vs audio paths:
    1. User enters URL
    2. System detects available formats
    3. User chooses VIDEO or AUDIO
    4. Video path: quality → codec → subtitles → send_as → downloading → uploading → done
    5. Audio path: format → downloading → uploading → done
    """
    
    # Initial state
    waiting_for_url = State()
    
    # Format type selection (Video vs Audio)
    selecting_format_type = State()
    
    # Video-specific states
    video_quality_selection = State()
    video_codec_selection = State()
    
    # Audio-specific states
    audio_format_selection = State()
    
    # Shared optional states
    selecting_subtitle = State()
    
    # Video-only states
    selecting_send_as = State()  # Video / Audio / Document
    
    # Common execution states
    selecting_format = State()  # Legacy - for backward compatibility
    confirming_download = State()
    downloading = State()
    uploading = State()
    completed = State()


__all__ = ["DownloadStates"]

