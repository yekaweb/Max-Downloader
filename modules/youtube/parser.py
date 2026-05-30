"""YouTube format parser - Extract and structure available formats"""
from typing import List, Dict, Any, Optional


def parse_formats(formats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse yt-dlp formats into user-friendly quality options.
    Groups by resolution and extracts best audio/video combinations.
    """
    if not formats:
        return []

    video_formats = []
    audio_formats = []
    combined_formats = []

    for fmt in formats:
        # Skip formats without format_id or those that can't be downloaded
        if not fmt.get("format_id") or fmt.get("format_note") == "storyboard":
            continue

        fmt_id = fmt.get("format_id")
        ext = fmt.get("ext", "unknown")
        filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)

        # Categorize formats
        has_video = fmt.get("vcodec") != "none" and fmt.get("width")
        has_audio = fmt.get("acodec") != "none"

        if has_video and has_audio:
            # Combined video + audio
            height = fmt.get("height", 0)
            fps = fmt.get("fps", 30)
            bitrate = fmt.get("tbr", 0)

            combined_formats.append(
                {
                    "format_id": fmt_id,
                    "ext": ext,
                    "type": "combined",
                    "label": f'{height}p@{fps}fps - {_format_size(filesize)}',
                    "resolution": f"{height}p",
                    "fps": fps,
                    "codec": fmt.get("vcodec", "unknown"),
                    "filesize": filesize,
                    "bitrate": bitrate,
                }
            )
        elif has_video:
            # Video only
            height = fmt.get("height", 0)
            fps = fmt.get("fps", 30)
            video_formats.append(
                {
                    "format_id": fmt_id,
                    "ext": ext,
                    "type": "video",
                    "label": f'{height}p@{fps}fps - {_format_size(filesize)}',
                    "resolution": f"{height}p",
                    "fps": fps,
                    "codec": fmt.get("vcodec", "unknown"),
                    "filesize": filesize,
                }
            )
        elif has_audio:
            # Audio only
            abr = fmt.get("abr", 128)
            acodec = fmt.get("acodec", "unknown")
            audio_formats.append(
                {
                    "format_id": fmt_id,
                    "ext": ext,
                    "type": "audio",
                    "label": f"{acodec} - {abr}kbps - {_format_size(filesize)}",
                    "bitrate": abr,
                    "codec": acodec,
                    "filesize": filesize,
                }
            )

    # Sort by quality (descending)
    combined_formats.sort(key=lambda x: x.get("resolution", "0p"), reverse=True)
    video_formats.sort(key=lambda x: x.get("resolution", "0p"), reverse=True)
    audio_formats.sort(key=lambda x: x.get("bitrate", 0), reverse=True)

    # Return combined first, then video, then audio
    result = combined_formats + video_formats + audio_formats

    # Limit to 20 most relevant formats
    return result[:20]


def get_format_for_quality(
    formats: List[Dict[str, Any]], quality: str, include_audio: bool = True
) -> Optional[str]:
    """
    Get format_id for a given quality preference.
    quality: "best", "good", "medium", "low", or specific like "720p"
    """
    if not formats:
        return None

    quality_map = {"best": 2160, "good": 1080, "medium": 720, "low": 360}
    target_height = quality_map.get(quality)

    # If specific resolution like "720p"
    if quality.endswith("p") and quality[:-1].isdigit():
        target_height = int(quality[:-1])

    # Filter combined formats (best quality)
    combined = [f for f in formats if f.get("type") == "combined"]

    if not combined:
        # Fallback to video + best audio
        video = [f for f in formats if f.get("type") == "video"]
        audio = [f for f in formats if f.get("type") == "audio"]

        if video and audio:
            # Find closest video resolution
            best_video = min(
                video,
                key=lambda x: abs(int(x.get("resolution", "0p")[:-1]) - target_height),
            )
            best_audio = audio[0]  # Best audio (first in sorted list)
            return f"{best_video['format_id']}+{best_audio['format_id']}"

    # Find closest resolution
    if combined:
        best = min(
            combined,
            key=lambda x: abs(int(x.get("resolution", "0p")[:-1]) - target_height),
        )
        return best["format_id"]

    return formats[0]["format_id"] if formats else None


def _format_size(bytes_size: int) -> str:
    """Convert bytes to human-readable format"""
    if not bytes_size:
        return "Unknown"

    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024

    return f"{bytes_size:.1f}TB"


__all__ = ["parse_formats", "get_format_for_quality"]
