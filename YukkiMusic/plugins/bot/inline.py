#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            InlineQueryResultPhoto)
from youtubesearchpython.__future__ import VideosSearch

from config import BANNED_USERS, MUSIC_BOT_NAME
from YukkiMusic import app
from YukkiMusic.utils.inlinequery import answer
from YukkiMusic.platforms.InnertubeClient import check_youtube_string
from YukkiMusic.platforms.Youtube_scrap import search_videos_with_post_api

@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    text = query.query.strip().lower()
    answers = []
    if text.strip() == "":
        try:
            await client.answer_inline_query(
                query.id, results=answer, cache_time=10
            )
        except:
            return
    else:
        #a = VideosSearch(text, limit=20)
       # result = (await a.next()).get("result")
        result,token=await search_videos_with_post_api(text)

        for x in range(len(result)):
            title = result[x].get("title","")
            duration = result[x].get("length","") if not None else 0
            views = result[x].get("views","")
            thumbnail = result[x].get("thumbnails", [{}])[0].get("url", "")
            channellink = f"https://youtube.com/@{result[x].get('channel','')}"
            channel = result[x].get("channel","")
            link = result[x].get("url","")
            published = result[x].get("publishedTime","")
            '''
            title = (result[x]["title"]).title()
            duration = result[x]["duration"]
            views = result[x]["viewCount"]["short"]
            thumbnail = result[x]["thumbnails"][0]["url"].split("?")[
                0
            ]
            channellink = result[x]["channel"]["link"]
            channel = result[x]["channel"]["name"]
            link = result[x]["link"]
            published = result[x]["publishedTime"]'''
            description = f"{views} | {duration} Mins | {channel}  | {published}"
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🎥 Watch on Youtube",
                            url=link,
                        )
                    ],
                ]
            )
            searched_text = f"""
❇️**Title:** [{title}]({link})

⏳**Duration:** {duration} Mins
👀**Views:** `{views}`
⏰**Published Time:** {published}
🎥**Channel Name:** {channel}
📎**Channel Link:** [Visit From Here]({channellink})

__Reply with /play on this searched message to stream it on voice chat.__

⚡️ ** Inline Search By {MUSIC_BOT_NAME} **"""
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=thumbnail,
                    title=title,
                    thumb_url=thumbnail,
                    description=description,
                    caption=searched_text,
                    reply_markup=buttons,
                )
            )
        try:
            return await client.answer_inline_query(
                query.id, results=answers
            )
        except:
            return
