"""FSM states for download flow with explicit video/audio branching"""
from aiogram.fsm.state import StatesGroup, State


class DownloadStates(StatesGroup):
    """
    Finite State Machine for complete download workflow.
    
    Flow:
    1. waiting_for_url - User sends URL
    2. selecting_format_type - Choose VIDEO or AUDIO
    3. Video path:
       - video_quality_selection - Select resolution (4K, 1080p, 720p, etc)
       - video_codec_selection - Select codec (H.264, AV1, VP9)
       - selecting_subtitle - Choose subtitle language or skip
       - selecting_send_as - Choose delivery method (Video/Document)
    4. Audio path:
       - audio_format_selection - Select audio format (MP3, AAC, OPUS)
    5. downloading - Download in progress
    6. uploading - Upload to Telegram
    7. completed - Done
    """
    
    # STEP 1: URL Reception
    waiting_for_url = State()
    
    # STEP 2: Format Type Selection (Video or Audio)
    selecting_format_type = State()
    
    # STEP 3: VIDEO PATH - Quality Selection
    video_quality_selection = State()
    
    # STEP 4: VIDEO PATH - Codec Selection
    video_codec_selection = State()
    
    # STEP 5: VIDEO PATH - Subtitle Selection (Optional)
    video_selecting_subtitle = State()
    
    # STEP 6: VIDEO PATH - Send As Selection
    video_selecting_send_as = State()
    
    # STEP 3: AUDIO PATH - Format Selection
    audio_format_selection = State()
    
    # STEP 4: AUDIO PATH - Subtitle Selection (Optional)
    audio_selecting_subtitle = State()
    
    # Execution states (common for both)
    downloading = State()
    uploading = State()
    completed = State()


__all__ = ["DownloadStates"]

