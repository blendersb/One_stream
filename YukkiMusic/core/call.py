#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.errors import (ChatAdminRequired, UserAlreadyParticipant,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (AlreadyJoinedError, NoActiveGroupCall)
from pytgcalls.types import (JoinedGroupCallParticipant,
                             LeftGroupCallParticipant, Update)
from pytgcalls.types.stream.legacy import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import MediaStream
from pytgcalls.types.stream import StreamAudioEnded

import config
from strings import get_string
from YukkiMusic import LOGGER, YouTube, app
from YukkiMusic.misc import db
from YukkiMusic.utils.database import (add_active_chat, add_active_video_chat,
                                       get_assistant, get_audio_bitrate,
                                       get_lang, get_loop, get_video_bitrate,
                                       group_assistant, is_autoend, music_on,
                                       mute_off, remove_active_chat,
                                       remove_active_video_chat, set_loop)
from YukkiMusic.utils.exceptions import AssistantErr
from YukkiMusic.utils.inline.play import (stream_markup, telegram_markup)
from YukkiMusic.utils.stream.autoclear import auto_clean
from YukkiMusic.utils.thumbnails import gen_thumb

autoend = {}
counter = {}
AUTO_END_TIME = 3


async def _clear_(chat_id):
  db[chat_id] = []
  await remove_active_video_chat(chat_id)
  await remove_active_chat(chat_id)


class Call(PyTgCalls):

  def __init__(self):
    self.userbot1 = Client(
        name="1",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=str(config.STRING1),
    )
    self.one = PyTgCalls(
        self.userbot1,
        cache_duration=100,
    )
    self.userbot2 = Client(
          name="2",
          api_id=config.API_ID,
          api_hash=config.API_HASH,
          session_string=str(config.STRING2),
        )
    self.two = PyTgCalls(
        self.userbot2,
        cache_duration=100,
    )
    self.userbot3 = Client(
        name="3",
          api_id=config.API_ID,
          api_hash=config.API_HASH,
          session_string=str(config.STRING3),
    )
    self.three = PyTgCalls(
        self.userbot3,
        cache_duration=100,
    )
    self.userbot4 = Client(
        name="4",
          api_id=config.API_ID,
          api_hash=config.API_HASH,
          session_string=str(config.STRING4),
    )
    self.four = PyTgCalls(
        self.userbot4,
        cache_duration=100,
    )
    self.userbot5 = Client(
        name="5",
          api_id=config.API_ID,
          api_hash=config.API_HASH,
          session_string=str(config.STRING5),
        
    )
    self.five = PyTgCalls(
        self.userbot5,
        cache_duration=100,
    )

  async def pause_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.pause_stream(chat_id)

  async def resume_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.resume_stream(chat_id)

  async def mute_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.mute_stream(chat_id)

  async def unmute_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.unmute_stream(chat_id)

  async def stop_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    try:
      await _clear_(chat_id)
      await assistant.leave_group_call(chat_id)
    except:
      pass

  async def force_stop_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    try:
      check = db.get(chat_id)
      check.pop(0)
    except:
      pass
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    try:
      await assistant.leave_group_call(chat_id)
    except:
      pass

  async def skip_stream(self,
                        chat_id: int,
                        link: str,
                        video: Union[bool, str] = None):
    assistant = await group_assistant(self, chat_id)
    audio_stream_quality = await get_audio_bitrate(chat_id)
    video_stream_quality = await get_video_bitrate(chat_id)
    stream = (AudioVideoPiped(
        link,
        audio_parameters=audio_stream_quality,
        video_parameters=video_stream_quality,
    ) if video else AudioPiped(link, audio_parameters=audio_stream_quality))
    await assistant.change_stream(
        chat_id,
        stream,
    )

  async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
    assistant = await group_assistant(self, chat_id)
    audio_stream_quality = await get_audio_bitrate(chat_id)
    video_stream_quality = await get_video_bitrate(chat_id)
    stream = (AudioVideoPiped(
        file_path,
        audio_parameters=audio_stream_quality,
        video_parameters=video_stream_quality,
        additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
    ) if mode == "video" else AudioPiped(
        file_path,
        audio_parameters=audio_stream_quality,
        additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
    ))
    await assistant.change_stream(chat_id, stream)

  async def stream_call(self, link):
    assistant = await group_assistant(self, config.LOG_GROUP_ID)
    await assistant.join_group_call(
        config.LOG_GROUP_ID,
        AudioVideoPiped(link),
        #stream_type=StreamType().pulse_stream,
    )
    await asyncio.sleep(0.5)
    await assistant.leave_group_call(config.LOG_GROUP_ID)
  #####################################################################################################
  '''async def live_call(self):
    assistant = await group_assistant(self, config.LOG_GROUP_ID)
    video_url="https://rr3---sn-gwpa-jj0k.googlevideo.com/videoplayback?expire=1720992868&ei=BPCTZo2hIcms9fwPxuiMoAQ&ip=34.93.83.202&id=o-AMlVXbysivqlwX1nPegSYVckA8UO6qOI1HNjA_C3ILVm&itag=137&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&bui=AXc671JgbdicNDMCvD64suPqy3V2hQF-GNxvsTkZ4Qpvo2dmu4bM_1b8SqzJ_I9_xQETqJurEz1vxgA2&vprv=1&mime=video%2Fmp4&rqh=1&gir=yes&clen=73860085&dur=221.916&lmt=1720511440920986&keepalive=yes&lmw=1&c=ANDROID_TV&txp=5532434&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cvprv%2Cmime%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAOjSd5GnA0fj9-jgOyQmW1sXSKx8WClSlO75pIYEZmjlAiEAkhn6qXR6My5_e1z4RBR6C6uGmYKrgaGnhWPYJ9S9ljc%3D&redirect_counter=1&rm=sn-cvh6l7e&fexp=24350516,24350518&req_id=f179ac02cc1ba3ee&cms_redirect=yes&cmsv=e&ipbypass=yes&mh=_i&mip=2409:40e1:1f:e1b6:6820:58cf:6a51:f4ca&mm=31&mn=sn-gwpa-jj0k&ms=au&mt=1720970964&mv=m&mvi=3&pl=48&lsparams=ipbypass,mh,mip,mm,mn,ms,mv,mvi,pl&lsig=AHlkHjAwRQIhAOJXJOUSYjnXhP8mIhp7BXilkWg27LhQwSgFo7h7Sqr9AiBFk9gtmm9mYJoANtxtJDYO92RdMgOq_AXd9D-mcxHuyw%3D%3D"
    audio_url="https://rr3---sn-gwpa-jj0k.googlevideo.com/videoplayback?expire=1720992868&ei=BPCTZo2hIcms9fwPxuiMoAQ&ip=34.93.83.202&id=o-AMlVXbysivqlwX1nPegSYVckA8UO6qOI1HNjA_C3ILVm&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&bui=AXc671JgbdicNDMCvD64suPqy3V2hQF-GNxvsTkZ4Qpvo2dmu4bM_1b8SqzJ_I9_xQETqJurEz1vxgA2&vprv=1&mime=audio%2Fwebm&rqh=1&gir=yes&clen=3994328&dur=221.941&lmt=1720508953333763&keepalive=yes&lmw=1&c=ANDROID_TV&txp=5532434&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cvprv%2Cmime%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgDKbPBz-4y2_EOaOVAA99AggLmKgrfnV21tW1KGXdPPICIQD3ZGqgy9ewLeEK2-WHYpE7P1-Lqm48qYyWOOwZzuvHCA%3D%3D&redirect_counter=1&rm=sn-cvh6l7e&fexp=24350516,24350518&req_id=877fdd961f2a3ee&cms_redirect=yes&cmsv=e&ipbypass=yes&mh=_i&mip=2409:40e1:1f:e1b6:6820:58cf:6a51:f4ca&mm=31&mn=sn-gwpa-jj0k&ms=au&mt=1720970964&mv=m&mvi=3&pl=48&lsparams=ipbypass,mh,mip,mm,mn,ms,mv,mvi,pl&lsig=AHlkHjAwRAIgJmYgFL-esOsvjZ0cLdtkGojJf2RAvyY3BghjEGHqxI4CIDMb2rdPML37UNGuGCZbrkwsKjgfI5FAZ3fOGO-3VO7X"

    await assistant.join_group_call(
        config.LOG_GROUP_ID,
        MediaStream(
          media_path=video_url,
          audio_path=audio_url,
        ),
        #stream_type=StreamType().pulse_stream,
    )
    
'''
  async def join_assistant(self, original_chat_id, chat_id):
    language = await get_lang(original_chat_id)
    _ = get_string(language)
    userbot = await get_assistant(chat_id)
    try:
      try:
        get = await app.get_chat_member(chat_id, userbot.id)
      except ChatAdminRequired:
        raise AssistantErr(_["call_1"])
      if get.status == "banned" or get.status == "kicked":
        raise AssistantErr(_["call_2"].format(userbot.username, userbot.id))
    except UserNotParticipant:
      chat = await app.get_chat(chat_id)
      if chat.username:
        try:
          await userbot.join_chat(chat.username)
        except UserAlreadyParticipant:
          pass
        except Exception as e:
          raise AssistantErr(_["call_3"].format(e))
      else:
        try:
          try:
            try:
              invitelink = chat.invite_link
              if invitelink is None:
                invitelink = (await app.export_chat_invite_link(chat_id))
            except:
              invitelink = (await app.export_chat_invite_link(chat_id))
          except ChatAdminRequired:
            raise AssistantErr(_["call_4"])
          except Exception as e:
            raise AssistantErr(e)
          m = await app.send_message(original_chat_id, _["call_5"])
          if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+",
                                            "https://t.me/joinchat/")
          await asyncio.sleep(3)
          await userbot.join_chat(invitelink)
          await asyncio.sleep(4)
          await m.edit(_["call_6"].format(userbot.name))
        except UserAlreadyParticipant:
          pass
        except Exception as e:
          raise AssistantErr(_["call_3"].format(e))

  async def join_call(
      self,
      chat_id: int,
      original_chat_id: int,
      link,
      video: Union[bool, str] = None,
  ):
    assistant = await group_assistant(self, chat_id)
    audio_stream_quality = await get_audio_bitrate(chat_id)
    video_stream_quality = await get_video_bitrate(chat_id)
    stream = (AudioVideoPiped(
        link,
        audio_parameters=audio_stream_quality,
        video_parameters=video_stream_quality,
    ) if video else AudioPiped(link, audio_parameters=audio_stream_quality))
    try:
      print("join call")
      await assistant.join_group_call(
          chat_id,
          stream,
          #stream_type=StreamType().pulse_stream,
      )
    except NoActiveGroupCall:
      try:
        await self.join_assistant(original_chat_id, chat_id)
      except Exception as e:
        raise e
      try:
        await assistant.join_group_call(
            chat_id,
            stream,
            #stream_type=StreamType().pulse_stream,
        )
      except Exception as e:
        raise AssistantErr(
            "**No Active Voice Chat Found**\n\nPlease make sure group's voice chat is enabled. If already enabled, please end it and start fresh voice chat again and if the problem continues, try /restart"
        )
    except AlreadyJoinedError:
      raise AssistantErr(
          "**Assistant Already in Voice Chat**\n\nSystems have detected that assistant is already there in the voice chat, this issue generally comes when you play 2 queries together.\n\nIf assistant is not present in voice chat, please end voice chat and start fresh voice chat again and if the  problem continues, try /restart"
      )
    '''except TelegramServerError:
      raise AssistantErr(
          "**Telegram Server Error**\n\nTelegram is having some internal server problems, Please try playing again.\n\n If this problem keeps coming everytime, please end your voice chat and start fresh voice chat again."
      )'''
    await add_active_chat(chat_id)
    await mute_off(chat_id)
    await music_on(chat_id)
    if video:
      await add_active_video_chat(chat_id)
    if await is_autoend():
      counter[chat_id] = {}
      users = len(await assistant.get_participants(chat_id))
      if users == 1:
        autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

  async def join_live_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
    ):
      assistant = await group_assistant(self, chat_id)
      audio_stream_quality = await get_audio_bitrate(chat_id)
      video_stream_quality = await get_video_bitrate(chat_id)
      '''stream = (AudioVideoPiped(
          link,
          audio_parameters=audio_stream_quality,
          video_parameters=video_stream_quality,
      ) if video else AudioPiped(link, audio_parameters=audio_stream_quality))'''
      try:
        print("join live call")
        if video:
          await assistant.join_group_call(
              chat_id,
              MediaStream(
                media_path=link,
                video_parameters=video_stream_quality,
              ),
              #stream_type=StreamType().pulse_stream,
          )
        else:
          await assistant.join_group_call(
              chat_id,
              MediaStream(
                media_path=link,
                audio_parameters=audio_stream_quality,
                #video_flags=MediaStream.Flags.IGNORE,
              ),
              #stream_type=StreamType().pulse_stream,
          )
      except NoActiveGroupCall:
        try:
          await self.join_assistant(original_chat_id, chat_id)
        except Exception as e:
          raise e
        try:
          if video:
            await assistant.join_group_call(
                chat_id,
                MediaStream(
                  media_path=link,
                  video_parameters=video_stream_quality,
                ),
                #stream_type=StreamType().pulse_stream,
            )
          else:
            await assistant.join_group_call(
                chat_id,
                MediaStream(
                  media_path=link,
                  audio_parameters=audio_stream_quality,
                  #video_flags=MediaStream.Flags.IGNORE,
                ),
                #stream_type=StreamType().pulse_stream,
            )
        except Exception as e:
          raise AssistantErr(
              "**No Active Voice Chat Found**\n\nPlease make sure group's voice chat is enabled. If already enabled, please end it and start fresh voice chat again and if the problem continues, try /restart"
          )
      except AlreadyJoinedError:
        raise AssistantErr(
            "**Assistant Already in Voice Chat**\n\nSystems have detected that assistant is already there in the voice chat, this issue generally comes when you play 2 queries together.\n\nIf assistant is not present in voice chat, please end voice chat and start fresh voice chat again and if the  problem continues, try /restart"
        )
      '''except TelegramServerError:
        raise AssistantErr(
            "**Telegram Server Error**\n\nTelegram is having some internal server problems, Please try playing again.\n\n If this problem keeps coming everytime, please end your voice chat and start fresh voice chat again."
        )'''
      await add_active_chat(chat_id)
      await mute_off(chat_id)
      await music_on(chat_id)
      if video:
        await add_active_video_chat(chat_id)
      if await is_autoend():
        counter[chat_id] = {}
        users = len(await assistant.get_participants(chat_id))
        if users == 1:
          autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)




  async def live_call(
          self,
          chat_id: int,
          original_chat_id: int,
          video_url,
          audio_url,
          video: Union[bool, str] = None,
      ):
        
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        '''stream = (AudioVideoPiped(
            link,
            audio_parameters=audio_stream_quality,
            video_parameters=video_stream_quality,
        ) if video else AudioPiped(link, audio_parameters=audio_stream_quality))'''
        try:
          print("live call")
          test_stream = 'http://docs.evostream.com/sample_content/assets/' \
              'sintel1m720p.mp4'
          if video:
            await assistant.join_group_call(
                chat_id,
                MediaStream(
                  media_path=video_url,
                  audio_path=audio_url,
                  audio_parameters=audio_stream_quality,
                  video_parameters=video_stream_quality,
                ),
                #stream_type=StreamType().pulse_stream,
            )
          else:
            await assistant.join_group_call(
                chat_id,
                MediaStream(
                  media_path=audio_url,
                  audio_parameters=audio_stream_quality,
                  #video_flags=MediaStream.Flags.IGNORE,
                ),
                #stream_type=StreamType().pulse_stream,
            )
        except NoActiveGroupCall:
          try:
            await self.join_assistant(original_chat_id, chat_id)
          except Exception as e:
            raise e
          try:
            print("live call")
            if video:
              await assistant.join_group_call(
                  chat_id,
                  MediaStream(
                    media_path=video_url,
                    audio_path=audio_url,
                    audio_parameters=audio_stream_quality,
                    video_parameters=video_stream_quality,
                  ),
                  #stream_type=StreamType().pulse_stream,
              )
            else:
              await assistant.join_group_call(
                  chat_id,
                  MediaStream(
                    media_path=audio_url,
                    audio_parameters=audio_stream_quality,
                    #video_flags=MediaStream.Flags.IGNORE,
                  ),
                  #stream_type=StreamType().pulse_stream,
              )
          except Exception as e:
            raise AssistantErr(
                "**No Active Voice Chat Found**\n\nPlease make sure group's voice chat is enabled. If already enabled, please end it and start fresh voice chat again and if the problem continues, try /restart"
            )
        except AlreadyJoinedError:
          raise AssistantErr(
              "**Assistant Already in Voice Chat**\n\nSystems have detected that assistant is already there in the voice chat, this issue generally comes when you play 2 queries together.\n\nIf assistant is not present in voice chat, please end voice chat and start fresh voice chat again and if the  problem continues, try /restart"
          )
        '''except TelegramServerError:
          raise AssistantErr(
              "**Telegram Server Error**\n\nTelegram is having some internal server problems, Please try playing again.\n\n If this problem keeps coming everytime, please end your voice chat and start fresh voice chat again."
          )'''
        await add_active_chat(chat_id)
        await mute_off(chat_id)
        await music_on(chat_id)
        if video:
          await add_active_video_chat(chat_id)
        if await is_autoend():
          counter[chat_id] = {}
          users = len(await assistant.get_participants(chat_id))
          if users == 1:
            autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

  async def change_stream(self, client, chat_id):
    check = db.get(chat_id)
    popped = None
    loop = await get_loop(chat_id)
    try:
      if loop == 0:
        popped = check.pop(0)
      else:
        loop = loop - 1
        await set_loop(chat_id, loop)
      if popped:
        if config.AUTO_DOWNLOADS_CLEAR == str(True):
          await auto_clean(popped)
      if not check:
        await _clear_(chat_id)
        return await client.leave_group_call(chat_id)
    except:
      try:
        await _clear_(chat_id)
        return await client.leave_group_call(chat_id)
      except:
        return
    else:
      queued = check[0]["file"]
      language = await get_lang(chat_id)
      _ = get_string(language)
      title = (check[0]["title"]).title()
      user = check[0]["by"]
      original_chat_id = check[0]["chat_id"]
      streamtype = check[0]["streamtype"]
      audio_stream_quality = await get_audio_bitrate(chat_id)
      video_stream_quality = await get_video_bitrate(chat_id)
      videoid = check[0]["vidid"]
      check[0]["played"] = 0
      if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
          return await app.send_message(
              original_chat_id,
              text=_["call_9"],
          )
        stream = (AudioVideoPiped(
            link,
            audio_parameters=audio_stream_quality,
            video_parameters=video_stream_quality,
        ) if str(streamtype) == "video" else AudioPiped(
            link, audio_parameters=audio_stream_quality))
        try:
          await client.change_stream(chat_id, stream)
        except Exception:
          return await app.send_message(
              original_chat_id,
              text=_["call_9"],
          )
        img = await gen_thumb(videoid)
        button = telegram_markup(_, chat_id)
        run = await app.send_photo(
            original_chat_id,
            photo=img,
            caption=_["stream_1"].format(
                user,
                f"https://t.me/{app.username}?start=info_{videoid}",
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
      elif "vid_" in queued:
        mystic = await app.send_message(original_chat_id, _["call_10"])
        try:
          file_path, direct = await YouTube.download(
              videoid,
              mystic,
              videoid=True,
              video=True if str(streamtype) == "video" else False,
          )
        except:
          return await mystic.edit_text(_["call_9"],
                                        disable_web_page_preview=True)
        stream = (AudioVideoPiped(
            file_path,
            audio_parameters=audio_stream_quality,
            video_parameters=video_stream_quality,
        ) if str(streamtype) == "video" else AudioPiped(
            file_path,
            audio_parameters=audio_stream_quality,
        ))
        try:
          await client.change_stream(chat_id, stream)
        except Exception:
          return await app.send_message(
              original_chat_id,
              text=_["call_9"],
          )
        img = await gen_thumb(videoid)
        button = stream_markup(_, videoid, chat_id)
        await mystic.delete()
        run = await app.send_photo(
            original_chat_id,
            photo=img,
            caption=_["stream_1"].format(
                user,
                f"https://t.me/{app.username}?start=info_{videoid}",
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
      elif "index_" in queued:
        stream = (AudioVideoPiped(
            videoid,
            audio_parameters=audio_stream_quality,
            video_parameters=video_stream_quality,
        ) if str(streamtype) == "video" else AudioPiped(
            videoid, audio_parameters=audio_stream_quality))
        try:
          await client.change_stream(chat_id, stream)
        except Exception:
          return await app.send_message(
              original_chat_id,
              text=_["call_9"],
          )
        button = telegram_markup(_, chat_id)
        run = await app.send_photo(
            original_chat_id,
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
      else:
        stream = (AudioVideoPiped(
            queued,
            audio_parameters=audio_stream_quality,
            video_parameters=video_stream_quality,
        ) if str(streamtype) == "video" else AudioPiped(
            queued, audio_parameters=audio_stream_quality))
        try:
          await client.change_stream(chat_id, stream)
        except Exception:
          return await app.send_message(
              original_chat_id,
              text=_["call_9"],
          )
        if videoid == "telegram":
          button = telegram_markup(_, chat_id)
          run = await app.send_photo(
              original_chat_id,
              photo=config.TELEGRAM_AUDIO_URL
              if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL,
              caption=_["stream_3"].format(title, check[0]["dur"], user),
              reply_markup=InlineKeyboardMarkup(button),
          )
          db[chat_id][0]["mystic"] = run
          db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
          button = telegram_markup(_, chat_id)
          run = await app.send_photo(
              original_chat_id,
              photo=config.SOUNCLOUD_IMG_URL,
              caption=_["stream_3"].format(title, check[0]["dur"], user),
              reply_markup=InlineKeyboardMarkup(button),
          )
          db[chat_id][0]["mystic"] = run
          db[chat_id][0]["markup"] = "tg"
        else:
          img = await gen_thumb(videoid)
          button = stream_markup(_, videoid, chat_id)
          run = await app.send_photo(
              original_chat_id,
              photo=img,
              caption=_["stream_1"].format(
                  user,
                  f"https://t.me/{app.username}?start=info_{videoid}",
              ),
              reply_markup=InlineKeyboardMarkup(button),
          )
          db[chat_id][0]["mystic"] = run
          db[chat_id][0]["markup"] = "stream"

  async def ping(self):
    pings = []
    if config.STRING1:
      pings.append(await self.one.ping)
    if config.STRING2:
      pings.append(await self.two.ping)
    if config.STRING3:
      pings.append(await self.three.ping)
    if config.STRING4:
      pings.append(await self.four.ping)
    if config.STRING5:
      pings.append(await self.five.ping)
    return str(round(sum(pings) / len(pings), 3))


  async def start(self):
    LOGGER(__name__).info("Starting PyTgCalls Client\n")
    if config.STRING1:
      await self.one.start()
    if config.STRING2:
      await self.two.start()
    if config.STRING3:
      await self.three.start()
    if config.STRING4:
      await self.four.start()
    if config.STRING5:
      await self.five.start()

  async def decorators(self):

    @self.one.on_kicked()
    @self.two.on_kicked()
    @self.three.on_kicked()
    @self.four.on_kicked()
    @self.five.on_kicked()
    @self.one.on_closed_voice_chat()
    @self.two.on_closed_voice_chat()
    @self.three.on_closed_voice_chat()
    @self.four.on_closed_voice_chat()
    @self.five.on_closed_voice_chat()
    @self.one.on_left()
    @self.two.on_left()
    @self.three.on_left()
    @self.four.on_left()
    @self.five.on_left()
    async def stream_services_handler(_, chat_id: int):
      await self.stop_stream(chat_id)

    @self.one.on_stream_end()
    @self.two.on_stream_end()
    @self.three.on_stream_end()
    @self.four.on_stream_end()
    @self.five.on_stream_end()
    async def stream_end_handler1(client, update: Update):
      if not isinstance(update, StreamAudioEnded):
        return
      await self.change_stream(client, update.chat_id)

    @self.one.on_participants_change()
    @self.two.on_participants_change()
    @self.three.on_participants_change()
    @self.four.on_participants_change()
    @self.five.on_participants_change()
    async def participants_change_handler(client, update: Update):
      if not isinstance(update, JoinedGroupCallParticipant) and not isinstance(
          update, LeftGroupCallParticipant):
        return
      chat_id = update.chat_id
      users = counter.get(chat_id)
      if not users:
        try:
          got = len(await client.get_participants(chat_id))
        except:
          return
        counter[chat_id] = got
        if got == 1:
          autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)
          return
        autoend[chat_id] = {}
      else:
        final = (users + 1 if isinstance(update, JoinedGroupCallParticipant)
                 else users - 1)
        counter[chat_id] = final
        if final == 1:
          autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)
          return
        autoend[chat_id] = {}

  

Yukki = Call()
