from innertube import InnerTube
from pprint import pprint
import re
# Rick Astley - Never Gonna Give You Up (Official Music Video)


# Client for YouTube on iOS
client = InnerTube("IOS")

YOUTUBE_REGEX = re.compile(
    r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
)

def check_youtube_string(s: str):
    # Check if it's a valid YouTube video ID (11 chars, letters/numbers/_/-)
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", s):
        return s
    
    # Check if it's a YouTube URL
    match = YOUTUBE_REGEX.match(s)
    if match:
        return match.group(1)
    
    return  None

def videoDetails(vid):
    video_id=check_youtube_string(vid)
    if video_id != None:
        try:
            data = client.player(video_id)
            print(data.get("videoDetails",{}))
            return data.get("videoDetails",{})
        except Exception as e:
            print(f"error-{e}")
    
def streamingData(vid):
    video_id=check_youtube_string(vid)
    if video_id != None:
        try:
            data = client.player(video_id)
            return data.get("streamingData",{}).get("adaptiveFormats",[])
        except Exception as e:
            print(f"error-{e}")


# Fetch the player data for the video


# List of streams of the video


# Print the list of streams
#pprint(data)