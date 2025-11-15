#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.
import os
import asyncio
import importlib
import logging

import sys
from aiohttp import web
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall
import signal
import config
from config import BANNED_USERS
from YukkiMusic import LOGGER, app, userbot
from YukkiMusic.alive import web_server
from YukkiMusic.core.call import Yukki
from YukkiMusic.plugins import ALL_MODULES
from YukkiMusic.utils.database import get_banned_users, get_gbanned

logging.basicConfig(level=logging.INFO)
#loop = asyncio.get_event_loop()
global loop
try:
    loop = asyncio.get_event_loop()
    
except RuntimeError:  # no running event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


server = web.AppRunner(web_server())

async def init():
    await server.setup()
    await web.TCPSite(server,'0.0.0.0', 7860).start()
    print("------------------------------Web Server Started ------------------------------")
    
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER("YukkiMusic").error(
            "No Assistant Clients Vars Defined!.. Exiting Process."
        )
        return
    if (
        not config.SPOTIFY_CLIENT_ID
        and not config.SPOTIFY_CLIENT_SECRET
    ):
        LOGGER("YukkiMusic").warning(
            "No Spotify Vars defined. Your bot won't be able to play spotify queries."
        )
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    clean_modules = [m.lstrip(".") for m in ALL_MODULES if isinstance(m, str) and m.strip()]
    for module in clean_modules:
        # If module already contains the package prefix, avoid double-prefixing
        if module.startswith("YukkiMusic.plugins"):
            full_name = module
        else:
            full_name = f"YukkiMusic.plugins.{module}"

        try:
            importlib.import_module(full_name)
            LOGGER("YukkiMusic.plugins").info("Imported: %s", full_name)
        except Exception as e:
            # Log exception but continue loading remaining plugins
            LOGGER("YukkiMusic.plugins").exception("Failed importing %s: %s", full_name, e)
    LOGGER("YukkiMusic.plugins").info("Finished importing modules")
    '''
    for all_module in ALL_MODULES:
        importlib.import_module("YukkiMusic.plugins" + all_module)
    LOGGER("Yukkimusic.plugins").info(
        "Successfully Imported Modules "
    )'''
    
    await userbot.start()
    await Yukki.start()
    
    try:
        await Yukki.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("YukkiMusic").error(
            "[ERROR] - \n\nPlease turn on your Logger Group's Voice Call. Make sure you never close/end voice call in your log group"
        )
        sys.exit()
    except Exception as e:
        print(e)
        
    #await Yukki.decorators()
    LOGGER("YukkiMusic").info("Yukki Music Bot Started Successfully")
    
    
    await idle()

async def cleanup():
    """Gracefully stop all running services."""
    print("\n------------------ Stopping Services -----------------")
    if server and server.sites:
        print("Stopping web server...")
        await server.cleanup()
        print("Web server stopped.")

    print("Stopping clients...")
    if app.is_initialized:
        await app.stop()
        print("Main client stopped.")
        #await Yukki.stop()
        #userbot.leave_chat(message.chat.id)
        print("User bot stopped.")
        await userbot.stop()
    
    
    # Stop all asyncio tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()  
    
    print("All tasks cancelled.")
    await asyncio.gather(*tasks, return_exceptions=True)
    if loop.is_running():
        loop.stop()
async def restart_program():
    """Perform a graceful restart."""
    print("\n------------------ Restarting Program ------------------")
    await cleanup()
    python = sys.executable
    os.execl(python, python, *sys.argv)  # Replace current process


def handle_signal(signum, frame):
    """Handle Unix signals for restart or shutdown."""
    if signum in getattr(signal, "SIGHUP", ()):
        logging.info(f"Received SIGHUP ({signum}) — performing hot restart...")
        asyncio.run(restart_program())
    elif signum in getattr(signal, "SIGUSR1", ()) or signum in getattr(signal, "SIGUSR2", ()):
        logging.info(f"Received user-defined signal ({signum}) — performing hot restart...")
        asyncio.run(restart_program())
    elif signum in (signal.SIGINT, signal.SIGTERM):
        logging.info(f"Received termination signal ({signum}) — shutting down gracefully...")
        asyncio.run(cleanup())
        sys.exit(0)
if __name__ == "__main__":
    #keep_alive()
    
    '''loop.run_until_complete(init())
    LOGGER("YukkiMusic").info("Stopping Yukki Music Bot! GoodBye")'''
    # Register signal handlers
    for sig_name in ["SIGHUP", "SIGUSR1", "SIGUSR2", "SIGTERM", "SIGINT"]:
        if hasattr(signal, sig_name):
            signal.signal(getattr(signal, sig_name), handle_signal)

    try:
        loop.run_until_complete(init())
        #loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("------------------------ Services Stopped ------------------------")
        
    except Exception as e:
        LOGGER("YukkiMusic").info(f"Stopping Yukki Music Bot! GoodBye--{e}")
        print(e)
        #LOGGER(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        try:
            # Run cleanup safely
            loop.run_until_complete(cleanup())
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception as e:
            print("Error while running cleanup in finally:", e)
        finally:
            if not loop.is_closed():
                loop.close()
            print("Application closed.")
            sys.exit(0)   # <-- Clean exit
            #os._exit(0)
