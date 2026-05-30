# FSM State Diagram - Download Workflow

## State Machine Architecture

```
┌─────────────────┐
│  waiting_for_url│ (Start)
└────────┬────────┘
         │ [User enters URL]
         ▼
┌──────────────────────────┐
│ selecting_format_type    │ (Branch point)
└────┬─────────────────┬───┘
     │ [Video]         │ [Audio]
     ▼                 ▼
┌────────────────────┐  ┌──────────────────┐
│ video_quality_sel. │  │ audio_format_sel.│
└────────┬───────────┘  └────────┬─────────┘
         │                       │
         ▼                       │
┌────────────────────┐           │
│ video_codec_sel.   │           │
└────────┬───────────┘           │
         │                       │
         ▼                       │
┌────────────────────┐           │
│ selecting_send_as  │           │
└────────┬───────────┘           │
         │                       │
         └───────┬───────────────┘
                 │ [Format decided]
                 ▼
        ┌──────────────────┐
        │ selecting_subitle│ (Optional)
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ confirming_download  │ (User confirms)
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ downloading          │ (Downloading media)
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ uploading            │ (Uploading to Telegram)
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ completed            │ (Done)
        └──────────────────────┘
```

## State Descriptions

### Initialization
- **waiting_for_url**: Initial state, waiting for user to provide URL

### Format Selection
- **selecting_format_type**: User chooses between VIDEO or AUDIO
  - Determines which path to follow
  - Should display inline buttons: [🎬 Video] [🎵 Audio]

### Video Branch
- **video_quality_selection**: User selects quality (1080p, 720p, 480p, etc.)
- **video_codec_selection**: User selects video codec (h264, vp9, av1)
- **selecting_send_as**: User chooses how to send (Video / Audio / Document)

### Audio Branch  
- **audio_format_selection**: User selects audio format (MP3, AAC, FLAC, WAV)

### Optional States
- **selecting_subtitle**: User can optionally add subtitles (shared by video/audio)

### Execution States
- **confirming_download**: Final confirmation before download starts
- **downloading**: Media is being downloaded from source
- **uploading**: Downloaded media is being uploaded to Telegram
- **completed**: Download and upload complete

### Legacy States (Backward Compatibility)
- **selecting_format**: Legacy format selection (kept for backward compatibility)
- **confirming_download**: Used in legacy flow

## Transitions

### Video Path
```
waiting_for_url 
  → selecting_format_type (VIDEO) 
  → video_quality_selection 
  → video_codec_selection 
  → selecting_send_as
  → selecting_subtitle (optional)
  → confirming_download
  → downloading
  → uploading
  → completed
```

### Audio Path
```
waiting_for_url 
  → selecting_format_type (AUDIO) 
  → audio_format_selection 
  → selecting_subtitle (optional)
  → confirming_download
  → downloading
  → uploading
  → completed
```

## Implementation Notes

1. **Explicit Branching**: The `selecting_format_type` state is the branch point
   - Video users: Navigate through VIDEO_* states
   - Audio users: Navigate through AUDIO_* states
   - Both merge at `selecting_subtitle`

2. **Optional States**: `selecting_subtitle` is optional
   - User can skip to `confirming_download`
   - But if they choose subtitles, they must go through it

3. **Send As Options**: Only for VIDEO
   - Video: Send as native video file
   - Audio: Send as native audio file  
   - Document: Send as document for archive

4. **Handler Implementation**: Handlers must explicitly check current state
   - Prevent invalid transitions (e.g., audio user shouldn't reach video_quality_selection)
   - Provide helpful error messages for invalid operations

## Testing Checklist

- [ ] Video path: URL → Format Type → Quality → Codec → Send As → Subtitles → Confirm → Download → Upload → Done
- [ ] Audio path: URL → Format Type → Format → Subtitles → Confirm → Download → Upload → Done
- [ ] Invalid transitions blocked (e.g., skip quality selection)
- [ ] State data preserved across transitions
- [ ] User can go back to previous state
- [ ] User can cancel at any point
- [ ] Timeout handling for long states
