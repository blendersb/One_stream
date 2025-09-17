#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import random
import string
from ast import ExceptHandler
import traceback
from pyrogram import filters
from pyrogram import enums
from pyrogram.types import (InlineKeyboardMarkup,InlineKeyboardButton,WebAppInfo, InputMediaPhoto,KeyboardButton,ReplyKeyboardMarkup,
                            Message)
from pytgcalls.exceptions import NoActiveGroupCall
#from pyrogram.raw.types import UpdateWebViewResultSent, UpdateWebPage
from pyrogram.raw import functions, types
from pytube import extract
import config
import json 
from config import BANNED_USERS, lyrical,WEBAPP_URI
from strings import get_command
from pyrogram.enums import ParseMode, ChatType
from YukkiMusic import (Apple, Resso, SoundCloud, Spotify, Telegram,
                        YouTube, app)
from strings import get_string
from YukkiMusic.utils.database import (get_cmode, get_lang,
                                       get_playmode, get_playtype,
                                       is_active_chat,
                                       is_commanddelete_on,
                                       is_served_private_chat)
from YukkiMusic.core.call import Yukki
from YukkiMusic.utils import seconds_to_min, time_to_seconds
from YukkiMusic.utils.channelplay import get_channeplayCB
from YukkiMusic.utils.database import is_video_allowed
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.decorators.play import PlayWrapper
from YukkiMusic.utils.formatters import formats
from YukkiMusic.utils.inline.play import (livestream_markup,
                                          playlist_markup,
                                          slider_markup, track_markup)
from YukkiMusic.utils.inline.playlist import botplaylist_markup
from YukkiMusic.utils.logger import play_logs
from YukkiMusic.utils.stream.stream import stream

# Command
WEB_APP = get_command("WEB_APP_COMMAND")


    
@app.on_message(
    filters.command(WEB_APP)
    & ~BANNED_USERS
)
async def send_webapp_button(client,message: Message):
    
    custom_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Open WebApp", web_app=WebAppInfo(url=WEBAPP_URI))]
        ],
        resize_keyboard=True  # Optional: resize the keyboard to fit the screen
    )

    # Send a message with the custom keyboard
    await message.reply_text("Click the button below to open the WebApp:", reply_markup=custom_keyboard)

@app.on_message(filters.service
)
async def raw_update_handler(client, message: Message):
    #print("Received a service message",message)
    if message.web_app_data:
        # Handling WebApp data
        web_app_data = str(message.web_app_data.data)
        split_data=web_app_data.split(' ')
        id=split_data[1]
        id=id.replace('"', '')
        id=id.replace("'", "")
        #split_data = web_app_data.split(':')
        print(f"WebApp data received: {web_app_data},{id}")
        if message.chat.type == ChatType.PRIVATE:
            user_idx = message.from_user.id
        else:
            user_idx = message.chat.id
        # You can process the web app data here
        #chat_id = message.peer.user_id if hasattr(message.peer, "user_id") else update.peer.chat_id
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        chat_id = config.LOG_GROUP_ID
        #video_url=f'https://www.youtube.com/watch?v={id}'
        details, track_id = await YouTube.track(id,True)
        streamtype = "nodownload"
        img = details["thumb"]
        cap = _["play_19"].format(
            details["title"],
            details["duration_min"],
        )
        check=split_data[0].replace('"', '')
        check=check.replace("'",'')
        check=check.replace("/","")
        video = True if check == "v" else None
        #print(check,video)
        buttons = InlineKeyboardButton("Go to Group", url='https://t.me/+MeO0kQmZ5ddiYmZl')
        await message.reply_photo(
            photo=img,
            caption=cap,
            reply_markup=InlineKeyboardMarkup([[buttons]]),
        )
        try:
            await stream(
                _,
                'mystic',
                user_id,
                details,
                chat_id,
                user_name,
                chat_id,
                video=video,
                streamtype=streamtype
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = (
                e
                if ex_type == "AssistantErr"
                else _["general_3"].format(ex_type)
            )
            return await client.send_message(user_idx, f"Received err: {err}")
        
        await play_logs(message, streamtype=streamtype)
        #await client.send_message(user_idx, f"Received WebApp data: {web_app_data}")



'''@app.on_raw_update()
async def handle_raw_updates(client, update, users, chats):
    print("update",update)
    if isinstance(update, types.UpdateWebViewResultSent):
        # Handle the WebView result here
        result = update.result
        # Do something with the result
        print(f"Received WebView result: {result}")

    if isinstance(update, types.UpdateWebPage):
        # Handle the WebPage update here
        webpage = update.webpage
        # Do something with the webpage
        print(f"Received WebPage update: {webpage}")
'''
