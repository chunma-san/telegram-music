#!/usr/bin/env python3

import asyncio
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events


BASE = Path(__file__).resolve().parent
ENV_FILE = BASE / ".env"
SESSION_DIR = BASE / "session"
STATE_FILE = BASE / "state.json"

load_dotenv(ENV_FILE)

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"].strip()

DOWNLOAD_DIR = Path(
    os.environ.get(
        "DOWNLOAD_DIR",
        str(BASE / "data" / "downloads"),
    )
)

SESSION_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

SESSION = SESSION_DIR / "music"


AUDIO_EXTENSIONS = {
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}


MIME_TO_EXTENSION = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",

    "audio/flac": ".flac",
    "audio/x-flac": ".flac",

    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/m4a": ".m4a",

    "audio/aac": ".aac",

    "audio/ogg": ".ogg",
    "application/ogg": ".ogg",

    "audio/opus": ".opus",

    "audio/wav": ".wav",
    "audio/x-wav": ".wav",

    "audio/x-ms-wma": ".wma",
}


def load_state():
    if not STATE_FILE.exists():
        return {"downloaded": []}

    try:
        return json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return {"downloaded": []}


def save_state(state):
    tmp = STATE_FILE.with_suffix(".tmp")

    tmp.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    tmp.replace(STATE_FILE)


def safe_filename(name):
    if not name:
        return ""

    name = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        name,
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    ).strip()

    return name[:220]


def get_audio_extension(message):
    """
    Determine the audio extension primarily from Telegram MIME metadata.
    """

    if not message.file:
        return None

    mime = (
        message.file.mime_type or ""
    ).lower().strip()

    # Explicitly reject video files.
    if mime.startswith("video/"):
        return None

    if mime in MIME_TO_EXTENSION:
        return MIME_TO_EXTENSION[mime]

    # Unknown audio MIME:
    # accept a known audio extension if Telegram supplied one.
    if mime.startswith("audio/"):
        ext = (
            message.file.ext or ""
        ).lower()

        if ext in AUDIO_EXTENSIONS:
            return ext

    return None


def is_audio(message):
    return get_audio_extension(message) is not None


def get_filename(message):
    if not message.file:
        return None

    correct_ext = get_audio_extension(message)

    if not correct_ext:
        return None

    original_name = message.file.name

    if original_name:
        name = safe_filename(original_name)

        path = Path(name)
        current_ext = path.suffix.lower()

        # Filename already has the correct audio extension.
        if current_ext == correct_ext:
            return name

        # Filename has another known audio extension.
        # Keep it instead of unnecessarily renaming it.
        if current_ext in AUDIO_EXTENSIONS:
            return name

        # Missing/broken extension:
        # remove suspicious extension and use the MIME-derived one.
        if current_ext:
            name = path.stem

        name = safe_filename(name)

        if not name:
            name = f"telegram-{message.id}"

        return f"{name}{correct_ext}"

    return f"telegram-{message.id}{correct_ext}"


state = load_state()

downloaded = set(
    str(x)
    for x in state.get("downloaded", [])
)


client = TelegramClient(
    str(SESSION),
    API_ID,
    API_HASH,
)


async def download_message(message):
    key = str(message.id)

    if key in downloaded:
        return False

    if not is_audio(message):
        return False

    filename = get_filename(message)

    if not filename:
        return False

    destination = DOWNLOAD_DIR / filename

    # Never overwrite an existing track.
    if destination.exists():
        stem = destination.stem
        suffix = destination.suffix

        destination = (
            DOWNLOAD_DIR
            / f"{stem} [tg-{message.id}]{suffix}"
        )

    print(
        f"⬇️  [{message.id}] "
        f"{filename} "
        f"({message.file.mime_type})",
        flush=True,
    )

    result = await message.download_media(
        file=str(destination)
    )

    if not result:
        print(
            f"❌ Download failed: {filename}",
            flush=True,
        )
        return False

    downloaded.add(key)

    state["downloaded"] = sorted(
        downloaded,
        key=lambda x: int(x),
    )

    save_state(state)

    print(
        f"✅ {destination.name}",
        flush=True,
    )

    return True


async def initial_sync(entity):
    print()
    print("================================")
    print(" Telegram Music Initial Sync")
    print("================================")
    print()
    print("Channel :", CHANNEL)
    print("Folder  :", DOWNLOAD_DIR)
    print()

    found = 0
    saved = 0

    async for message in client.iter_messages(
        entity,
        reverse=True,
    ):
        if not is_audio(message):
            continue

        found += 1

        try:
            if await download_message(message):
                saved += 1

        except Exception as e:
            print(
                f"❌ Message {message.id}: "
                f"{type(e).__name__}: {e}",
                flush=True,
            )

    print()
    print("Initial sync finished.")
    print("Audio found :", found)
    print("Downloaded  :", saved)
    print()
    print("👀 Waiting for new tracks...")


async def main():
    await client.start()

    me = await client.get_me()

    print(
        f"✅ Telegram login: "
        f"{me.first_name or ''}",
        flush=True,
    )

    entity = await client.get_entity(
        CHANNEL
    )

    print(
        f"✅ Channel found: "
        f"{getattr(entity, 'title', CHANNEL)}",
        flush=True,
    )

    @client.on(
        events.NewMessage(chats=entity)
    )
    async def new_track(event):
        try:
            if is_audio(event.message):
                print()
                print(
                    "🆕 New audio received",
                    flush=True,
                )

                await download_message(
                    event.message
                )

        except Exception as e:
            print(
                f"❌ New message error: "
                f"{type(e).__name__}: {e}",
                flush=True,
            )

    await initial_sync(entity)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
