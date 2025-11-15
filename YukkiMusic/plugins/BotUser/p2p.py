from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import AudioQuality
from pytgcalls.types import Device
from pytgcalls.types import Direction
from pytgcalls.types import RecordStream
from pytgcalls.types import StreamFrames
from pytgcalls import filters as fl
from pytgcalls import PyTgCalls
from pytgcalls.types import ChatUpdate
from pyrogram.errors import UserPrivacyRestricted, Timeout
from YukkiMusic.core.call import Yukki
from YukkiMusic import userbot , app
#from YukkiMusic.utils.AI import AIModel

UserBotOne=userbot.one
AssistanceOne=Yukki.one
test_stream = 'http://docs.evostream.com/sample_content/assets/' \
              'sintel1m720p.mp4'
AUDIO_QUALITY = AudioQuality.HIGH
#model = AIModel(AUDIO_QUALITY)


@app.on_message(filters.regex('/call'))
async def play_handler(_: Client, message: Message):
    print(message)
    try:
        await AssistanceOne.play(
            message.chat.id,
            test_stream,)
    except UserPrivacyRestricted:
        await message.reply_text(
            "I couldn't call you because your Telegram privacy settings prevent incoming calls. "
        "Please set Calls -> Everybody (or allow me) and try again.",
        )
    except Timeout:
        await AssistanceOne.mtproto_client.send_message(
            message.chat.id,
            "You missed a call !!\nTimeout to answer",
        )
        await message.reply_text("You missed a call !!\nTimeout to answer")

@app.on_message(filters.regex('/hangup'))
async def stop_handler(_: Client, message: Message):
    await AssistanceOne.leave_call(
        message.chat.id,
    )

# @app.on_message(filters.regex('/ai'))
# async def AI_handler(_: Client, message:Message):
#     await AssistanceOne.record(
#     message.chat.id,
#     RecordStream(
#         True,
#         AUDIO_QUALITY,
#     ),
# )

# @AssistanceOne.on_update(
#     fl.stream_frame(
#         Direction.INCOMING,
#         Device.MICROPHONE,
#     ),
# )
# async def audio_data(_: PyTgCalls, update: StreamFrames):
#     # Transcribe just one user
#     stt = model.transcribe(update.frames[0].frame)
#     if stt:
#         print(stt, flush=True)   


@AssistanceOne.on_update(fl.chat_update(ChatUpdate.Status.INCOMING_CALL))
async def incoming_call_handler(_: PyTgCalls, update: ChatUpdate):
    
    await AssistanceOne.mtproto_client.send_message(
        update.chat_id,
        'You are calling me!',
    )
    await AssistanceOne.play(
        update.chat_id,
        test_stream,
    )

'''@AssistanceOne.on_update()
async def update_handler(_: PyTgCalls, update: ChatUpdate):
    print(update)'''
    
