#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import re
from typing import Union, List, Dict, Any, Optional
import math
import aiohttp
import yt_dlp
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from .InnertubeClient import videoDetails,streamingData
import scrapetube
from innertube import InnerTube
from pprint import pprint
from .Youtube_scrap import search_player_data_with_post_api
from YukkiMusic.utils.database.memorydatabase import audio as audio_settings, video as video_settings
import config
from YukkiMusic.utils.database import is_on_off
from YukkiMusic.utils.formatters import time_to_seconds ,seconds_to_min


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if (
            "unavailable videos are hidden"
            in (errorz.decode("utf-8")).lower()
        ):
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    async def exists(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == "url":
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == "text_link":
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link1 = self.base + link
        if "&" in link:
            link1 = link.split("&")[0]
        result=videoDetails(link)
        title = result.get("title","")
        duration_sec = result.get("lengthSeconds","") if not None else 0
        thumbnail = result.get("thumbnail", {}).get("thumbnails", [])[0].get("url")
        vidid = result.get("videoId","")
         
        '''
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
                '''
        return title, seconds_to_min(duration_sec), duration_sec, thumbnail, vidid

    async def title(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        result=videoDetails(link)
        title = result.get("title","")
    
        '''
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]'''
        return title

    async def duration(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        result=videoDetails(link)
        duration_sec = result.get("lengthSeconds","") if not None else 0
        
        '''    
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration'''
        return seconds_to_min(duration_sec)

    async def thumbnail(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        result=videoDetails(link)
        thumbnail = result.get("thumbnail", {}).get("thumbnails", [])[0].get("url")
        
        '''
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]'''
        return thumbnail

    async def video(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(
        self, link, limit, user_id, videoid: Union[bool, str] = None
    ):
        if videoid:
            link1 = self.listbase + link
        if "&" in link:
            link1 = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        result=videoDetails(link)
        title = result.get("title","")
        duration_sec = result.get("lengthSeconds","") if not None else 0
        thumbnail = result.get("thumbnail", {}).get("thumbnails", [])[0].get("url")
        vidid = result.get("videoId","")

        '''    
        results = VideosSearch(link, limit=1)
        #results = scrapetube.get_search(link,limit=1)
        for result in (await results.next())["result"]:
            #print(result)
            title = result["id"] if result["title"]=='' else result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]'''
        track_details = {
            "title": title,
            "link": f"https://www.youtube.com/watch?v={vidid}",
            "vidid": vidid,
            "duration_min": seconds_to_min(duration_sec),
            "thumb": thumbnail,
        }

   
        '''
        for result in results:
            print(result)
            title = result['title']['runs']['text']
            duration_min = result['lengthText']['simpleText']
            vidid = result['videoId']
            yturl = link
            thumbnail = result['thumbnail']['thumbnails'][0]['url']

            
        track_details = {
                "title":title ,
                "link": link,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }'''
        return track_details, vidid

    async def formats(
        self, link: str, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        result=videoDetails(link)
        title = result.get("title","")
        duration_sec = result.get("lengthSeconds","") if not None else 0
        thumbnail = result.get("thumbnail", {}).get("thumbnails", [])[0].get("url")
        vidid = result.get("videoId","")    
        '''
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split(
            "?"
        )[0]'''
        return title, seconds_to_min(duration_sec), thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def audio_dl():
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join(
                "downloads", f"{info['id']}.{info['ext']}"
            )
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join(
                "downloads", f"{info['id']}.{info['ext']}"
            )
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            return fpath
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath
        elif video:
            if await is_on_off(config.YTDOWNLOADER):
                direct = True
                downloaded_file = await loop.run_in_executor(
                    None, video_dl
                )
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    f"{link}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = None
                else:
                    return
        else:
            direct = True
            downloaded_file = await loop.run_in_executor(
                None, audio_dl
            )
        return downloaded_file, direct
    async def audio_video_url(self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            video_id= link
        loop = asyncio.get_running_loop()
        
        def get_audio_url():
            #yclient = InnerTube("ANDROID_TV")
            yclient = InnerTube("ANDROID_TV")
            # Fetch the player data for the video
            data = yclient.player(video_id)

            # List of streams of the video
            streams = data["streamingData"]["adaptiveFormats"]
            for stream in streams:
                if stream["mimeType"].find('video'):
                    audio_url=stream['url']
                    break
                else:
                    continue
            return audio_url
        def get_video_url():

            #yclient = InnerTube("ANDROID_TV")
            yclient = InnerTube("ANDROID_TV")

            
            # Fetch the player data for the video
            data = yclient.player(video_id)

            # List of streams of the video
            streams = data["streamingData"]["adaptiveFormats"]
            for stream in streams:
                if stream["mimeType"].find('audio'):
                    video_url=stream['url']
                    break
                else:
                    continue
            return video_url
        video_url = await loop.run_in_executor(
                    None, get_video_url
                )
        audio_url = await loop.run_in_executor(
                    None, get_audio_url
                )
        
        return video_url, audio_url
    ################################ for selecting audio video quality #########################
    async def _safe_int(self,v):
        try:
            return int(v) if v is not None else 0
        except Exception:
            return 0

    async def pick_video_audio_urls(self,formats: List[Dict[str, Any]]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Given a list of format dicts (each dict like your examples), return a mapping:
        {
        "video_high": {...}, "video_med": {...}, "video_low": {...},
        "audio_high": {...}, "audio_med": {...}, "audio_low": {...}
        }
        Each value is the selected format dict (or None).
        """
        if not formats:
            return {k: None for k in (
                "video_high","video_med","video_low",
                "audio_high","audio_med","audio_low"
            )}

        # Separate video and audio entries
        video_formats = []
        audio_formats = []

        for f in formats:
            f_copy = dict(f)  # avoid mutating original
            # normalize numeric fields
            f_copy["_height"] = await self._safe_int(f.get("height"))
            f_copy["_width"] = await self._safe_int(f.get("width"))
            f_copy["_bitrate"] = await self._safe_int(f.get("bitrate"))
            # Determine type: prefer explicit 'type' then check ext/formatId/is_audio
            ftype = (f.get("type") or "").lower()
            ext = (f.get("ext") or "").lower()
            if ftype == "video" and ext =="mp4":
                video_formats.append(f_copy)
            elif ftype == "audio" and ext == "m4a":
                audio_formats.append(f_copy)
            else:
                # fallback heuristics: some entries are video+audio (like mp4 itag 18)
                # treat entries with height>0 as video, with width/height==0 and bitrate>0 as audio
                if f_copy["_height"] > 0:
                    video_formats.append(f_copy)
                elif f_copy.get("is_audio") or (f_copy["_height"] == 0 and f_copy["_bitrate"] > 0 and f.get("mimeType","").startswith("audio")):
                    audio_formats.append(f_copy)
                else:
                    # if unknown, try to classify by extension: webm/mp4 usually video, opus/mp3/ogg usually audio
                    ext = (f.get("ext") or "").lower()
                    if ext in ("mp4"):
                        video_formats.append(f_copy)
                    elif ext in ("m4a"):
                        audio_formats.append(f_copy)
                    else:
                        # if still ambiguous, put into video if it has height, else audio if no height
                        if f_copy["_height"] > 0:
                            video_formats.append(f_copy)
                        else:
                            audio_formats.append(f_copy)

        # Sort video by height then bitrate (descending)
        video_formats.sort(key=lambda x: (x["_height"], x["_bitrate"]), reverse=True)
        # Sort audio by bitrate (descending)
        audio_formats.sort(key=lambda x: x["_bitrate"], reverse=True)

        async def pick_three(sorted_list):
            """Return high, med, low from a descending-sorted list."""
            if not sorted_list:
                return (None, None, None)
            n = len(sorted_list)
            high = sorted_list[0]
            low = sorted_list[-1]
            if n == 1:
                med = None
            elif n == 2:
                med = sorted_list[1]  # treat second as med
            else:
                # pick middle element as med
                med = sorted_list[n//2]
            return (high, med, low)

        v_high, v_med, v_low = await pick_three(video_formats)
        a_high, a_med, a_low = await pick_three(audio_formats)

        result = {
            "video_high": v_high,
            "video_med": v_med,
            "video_low": v_low,
            "audio_high": a_high,
            "audio_med": a_med,
            "audio_low": a_low,
        }

        # For convenience, also add direct URL strings (or None)
        for k, val in list(result.items()):
            result[k + "_url"] = None if val is None else val.get("url")

        return result
    async def audio_video_url_new(self,
        chat_id: str,                          
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            video_id= link
        loop = asyncio.get_running_loop()
        strem_list = await search_player_data_with_post_api(video_id)
        chosen = await self.pick_video_audio_urls(strem_list)
        #print("raw list",strem_list, chosen)
        def get_video_url():
            mode=video_settings.get(chat_id)
            if str(mode) == "High":
                return chosen["video_high_url"]
            elif str(mode) == "Medium":
                return chosen["video_med_url"]
            elif str(mode) == "Low":
                return chosen["video_low_url"]
            else:
                return chosen["video_med_url"]
            '''for stream in strem_list:
                if stream["type"].find('video') and str(mode) == "High":
                    video_url=stream['url']
                    break
                else:
                    continue
            return video_url'''
        def get_audio_url():

            mode=audio_settings.get(chat_id)
            if str(mode) == "High":
                return chosen["audio_high_url"]
            elif str(mode) == "Medium":
                return chosen["audio_med_url"]
            elif str(mode) == "Low":
                return chosen["audio_low_url"]
            else:
                return chosen["audio_med_url"]
            '''for stream in strem_list:
                if stream["type"].find('audio'):
                    audio_url=stream['url']
                    break
                else:
                    continue
            return audio_url'''
        video_url = await loop.run_in_executor(
                    None, get_video_url
                )
        audio_url = await loop.run_in_executor(
                    None, get_audio_url
                )
        print("video_url:",video_url,"\n audio_url:",audio_url )
        return  video_url,audio_url
