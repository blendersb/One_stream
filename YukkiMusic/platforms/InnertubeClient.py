import asyncio
from innertube import InnerTube
import re


# Client for YouTube on WEB (could also use "IOS" or "ANDROID")
client = InnerTube("WEB")

YOUTUBE_REGEX = re.compile(
    r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
)

def check_youtube_string(s: str):
    """Return YouTube video ID if string is ID or URL, else None."""
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", s):
        return s
    match = YOUTUBE_REGEX.match(s)
    if match:
        return match.group(1)
    return None

# ------------------------
# Async wrappers
# ------------------------
async def videoDetails(vid):
    """Return videoDetails dict for a video ID or URL."""
    video_id = check_youtube_string(vid)
    if not video_id:
        return {}

    try:
        data = await asyncio.to_thread(client.player, video_id)
        return data.get("videoDetails", {})
    except Exception as e:
        print(f"❌ Error fetching videoDetails: {e}")
        return {}

async def streamingData(vid):
    """Return adaptiveFormats list for a video ID or URL."""
    video_id = check_youtube_string(vid)
    if not video_id:
        return []

    try:
        data = await asyncio.to_thread(client.player, video_id)
        return data.get("streamingData", {}).get("adaptiveFormats", [])
    except Exception as e:
        print(f"❌ Error fetching streamingData: {e}")
        return []

# ------------------------
# Example usage
# ------------------------

