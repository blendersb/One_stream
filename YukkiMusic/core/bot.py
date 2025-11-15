import sys
import os
import tempfile
import shutil
import logging
import asyncio
from pyrogram import Client
from pyrogram.types import BotCommand
import config  # your config.py

# ---------- Logger Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("YukkiBot")

# ---------- Session Directory ----------
def resolve_session_dir(default_rel="/tmp/YukkiBot", app_name="YukkiBot"):
    """
    Resolve a writable session folder for Pyrogram.
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

# ---------- Bot Class ----------
class YukkiBot(Client):
    def __init__(self):
        # Resolve session directory
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

        # Send startup message
        try:
            await self.send_message(config.LOG_GROUP_ID, "Bot Started ✅")
        except Exception:
            log.error("Cannot access log group. Add bot to log channel & promote as admin!")
            sys.exit(1)

        # Set bot commands
        if str(config.SET_CMDS).lower() == "true":
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
            except Exception as e:
                log.warning(f"Failed to set bot commands: {e}")

        # Store full name
        self.name = f"{me.first_name} {me.last_name}" if me.last_name else me.first_name
        log.info(f"MusicBot Started as {self.name} (@{self.username})")

# ---------- Main ----------
async def main():
    bot = YukkiBot()
    await bot.start()
    log.info("Bot is now running. Press Ctrl+C to stop.")
    await asyncio.Event().wait()  # Keep running

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped manually.")
