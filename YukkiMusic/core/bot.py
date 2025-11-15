#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import sys

from pyrogram import Client
from pyrogram.types import BotCommand

import config

from ..logging import LOGGER


class YukkiBot(Client):

  def __init__(self):
    LOGGER(__name__).info(f"Starting Bot")
    super().__init__(
        "YukkiMusicBot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
    )

  async def start(self):
    await super().start()
    get_me = await self.get_me()
    self.username = get_me.username
    self.id = get_me.id
    try:
      await self.send_message(config.LOG_GROUP_ID, "Bot Started")
    except:
      LOGGER(__name__).error(
          "Bot has failed to access the log Group. Make sure that you have added your bot to your log channel and promoted as admin!"
      )
      sys.exit()
    if config.SET_CMDS == str(True):
      try:
        await self.set_bot_commands([
            BotCommand("start","ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
            BotCommand("play", "ᴘʟᴀʏ ᴀꜱ ᴀᴜᴅɪᴏ"),
            BotCommand("vplay", "ᴘʟᴀʏ ᴀꜱ ᴠɪᴅᴇᴏ"),
            BotCommand("pause", "ᴘᴀᴜꜱᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏɪɴɢ ꜱᴏɴɢ"),
            BotCommand("resume", "Resume the paused song"),
            BotCommand("stop", "ʀᴇꜱᴜᴍᴇ ᴛʜᴇ ᴘᴀᴜꜱᴇᴅ ꜱᴏɴɢ"),
            BotCommand("end", "ᴄʟᴇᴀʀ ᴛʜᴇ Qᴜᴇᴜᴇ ᴀɴᴅ ʟᴇᴀᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"),
            BotCommand("ping", "ᴄʜᴇᴄᴋ ᴛʜᴀᴛ ʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ"),
            BotCommand("webapp",
                       "ᴏᴘᴇɴ ᴡᴇʙᴀᴘᴘ ᴏɴ ʏᴏᴜʀ ᴄʜᴀᴛ."),
            BotCommand("AI", "ᴀɪ ᴄᴀʟʟ"),
            #BotCommand("skip", "Moves to the next track in queue"),
            
            
            
            #BotCommand("shuffle", "Randomly shuffles the queued playlist."),
            BotCommand(
                "playmode",
                "ᴀʟʟᴏᴡꜱ ʏᴏᴜ ᴛᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇ ᴅᴇꜰᴀᴜʟᴛ ᴘʟᴀʏᴍᴏᴅᴇ ꜰᴏʀ ʏᴏᴜʀ ᴄʜᴀᴛ"),
            BotCommand("settings",
                       "ᴏᴘᴇɴ ᴛʜᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴏꜰ ᴛʜᴇ ᴍᴜꜱɪᴄ ʙᴏᴛ ꜰᴏʀ ʏᴏᴜʀ ᴄʜᴀᴛ")
        ])
      except:
        pass
    else:
      pass
    a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
    #print(a)
    '''if a.status != "ChatMemberStatus.ADMINISTRATOR":
            LOGGER(__name__).error(
                "Please promote Bot as Admin in Logger Group"
            )
            sys.exit()'''
    if get_me.last_name:
      self.name = get_me.first_name + " " + get_me.last_name
    else:
      self.name = get_me.first_name
    LOGGER(__name__).info(f"MusicBot Started as {self.name}")

