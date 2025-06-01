import os
import asyncio
from typing import Optional

async def compress_video_av1(input_path: str) -> Optional[str]:
    """Compress video using AV1 codec"""
    output_path = f"compressed_{os.path.basename(input_path)}.mkv"
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libsvtav1",      # AV1 encoding
        "-crf", "30",             # Quality (0-63)
        "-preset", "6",           # Speed/quality tradeoff
        "-g", "240",              # Keyframe interval
        "-svtav1-params", "tune=0",  # Optimize for VMAF
        "-c:a", "libopus",        # Audio codec
        "-b:a", "128k",           # Audio bitrate
        "-vbr", "on",            # Variable bitrate
        "-threads", "2",         # Limit CPU usage
        output_path
    ]
    
    proc = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    _, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        print(f"FFmpeg error: {stderr.decode()}")
        return None
    
    return output_path if os.path.exists(output_path) else None
