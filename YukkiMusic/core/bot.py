import sys
import os
import tempfile
import shutil
import logging
from pyrogram import Client
from pyrogram.types import BotCommand
import config  # your config.py

log = logging.getLogger(__name__)

def resolve_session_dir(default_rel="./sessions", app_name="YukkiBot"):
    """
    Resolve a writable sessions folder for Pyrogram.
    Returns absolute folder path.
    """
    original = os.path.abspath(default_rel)
    main_original = os.path.join(original, "clients_sessions")

    # Try to create original folder and test writability
    try:
        os.makedirs(main_original, exist_ok=True)
        test_file = os.path.join(main_original, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        log.info("Using sessions dir: %s", main_original)
        return main_original
    except Exception as e:
        log.warning("Original sessions dir %s not writable: %s", main_original, e)

    # Fallback to /tmp/<app_name>/clients_sessions
    fallback = os.path.join(tempfile.gettempdir(), app_name, "clients_sessions")
    os.makedirs(fallback, exist_ok=True)

    # Copy any existing sessions from original if possible
    if os.path.isdir(main_original):
        try:
            for filename in os.listdir(main_original):
                src_path = os.path.join(main_original, filename)
                dst_path = os.path.join(fallback, filename)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
            log.info("Copied existing session files to fallback: %s", fallback)
        except Exception as e:
            log.warning("Failed to copy session files: %s", e)

    log.info("Using fallback sessions dir: %s", fallback)
    return fallback


class YukkiBot(Client):
    def __init__(self):
        session_path = resolve_session_dir()
        session_file = os.path.join(session_path, "YukkiMusicBot.session")
        log.info(f"Starting Bot with session: {session_file}")

        super().__init__(
            session_file,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        try:
            await self.send_message(config.LOG_GROUP_ID, "Bot Started")
        except Exception:
            log.error(
                "Bot cannot access the log group. Add it and promote as admin!"
            )
            sys.exit()

        # Set bot commands
        if config.SET_CMDS == "True":
            try:
                await self.set_bot_commands([
                    BotCommand("start","Start the bot"),
                    BotCommand("play", "Play audio"),
                    BotCommand("vplay", "Play video"),
                    BotCommand("pause", "Pause current song"),
                    BotCommand("resume", "Resume paused song"),
                    BotCommand("stop", "Stop current song"),
                    BotCommand("end", "Clear queue and leave voice chat"),
                    BotCommand("ping", "Check bot status"),
                    BotCommand("webapp","Open web app"),
                    BotCommand("AI", "AI call"),
                    BotCommand("playmode","Change default playmode"),
                    BotCommand("settings","Open bot settings"),
                ])
            except Exception:
                pass

        # Store full name
        if me.last_name:
            self.name = f"{me.first_name} {me.last_name}"
        else:
            self.name = me.first_name

        log.info(f"MusicBot Started as {self.name}")
