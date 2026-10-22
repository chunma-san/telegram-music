<!-- CAT-COUNTER:START -->
<p align="center">
  <img src="https://count.himiku.com/@chunma-telegram-music-3bf271?theme=capoo-2&amp;padding=6&amp;scale=0.8&amp;darkmode=1" alt="Cute cat project visits counter" />
</p>


<!-- CAT-COUNTER:END -->

<!-- typing-title:start -->
<p align="center">
  <a href="https://github.com/DenverCoder1/readme-typing-svg">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&amp;weight=600&amp;size=28&amp;duration=3500&amp;pause=1800&amp;color=EF4444&amp;center=true&amp;vCenter=true&amp;width=760&amp;height=65&amp;repeat=true&amp;lines=Great+Love+Immortal+Venerable;Heaven+Refining+Demon+Venerable" alt="Great Love Immortal Venerable / Heaven Refining Demon Venerable" />
  </a>
</p>
<!-- typing-title:end -->

<!-- discord-presence:start -->
<p align="center">
  <a href="https://discord.com/users/891081797318897715">
    <img src="https://lanyard.cnrad.dev/api/891081797318897715?theme=dark&amp;bg=100b0d&amp;borderRadius=16px&amp;showDisplayName=true&amp;animated=true&amp;animatedDecoration=true" alt="Discord profile and live activity" />
  </a>
</p>
<!-- discord-presence:end -->

<!-- project-navigation:start -->
<p align="center"><a href="https://github.com/chunma-san">Profile &amp; projects</a> · <a href="#quick-start">Quick start</a> · <a href="https://github.com/chunma-san/telegram-music/issues">Issues</a></p>
<!-- project-navigation:end -->

# Telegram Music

A Telethon client that saves audio from a configured Telegram source and tracks processed items.

**Runtime:** Python 3.11+ · **Configuration:** environment variables · **Deployment:** self-hosted

## Quick start

The supported deployment target is Linux. Create an isolated Python environment:

```sh
python3 -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env first. Use shell-compatible quoting for JSON and values with spaces.
set -a
. ./.env
set +a
python telegram_music.py
```

Only source a configuration file you created and trust. Starting the application can connect to external services; configure credentials and destinations first.

## Usage

Create Telegram API credentials, fill TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_CHANNEL locally, and run the script interactively for the first sign-in. The session is then reused for subsequent runs. DOWNLOAD_DIR selects the destination.

## Configuration

`.env.example` contains placeholders only. Real credentials, IDs, storage locations and account settings belong in your private local configuration.

| Variable | Requirement |
| --- | --- |
| `DOWNLOAD_DIR` | Directory for Telegram audio downloads. |
| `TELEGRAM_API_HASH` | Telegram API application secret. |
| `TELEGRAM_API_ID` | Telegram API application ID. |
| `TELEGRAM_CHANNEL` | Channel or source accessible to the signed-in Telegram account. |

## How it works and operational notes

This uses a Telegram user session, not a BotFather bot token. Keep `session/`, `state.json`, downloaded audio and your API credentials private. The account must be authorized to access the configured source.

## Project layout

- Source files implement the application and integrations.
- `requirements.txt` or the project file declares dependencies.
- `.env.example` documents configuration names without live values.
- `.gitignore` excludes credentials, sessions, generated data and build output.

## Verification

See [VALIDATION.md](VALIDATION.md) for the checks performed on this publication snapshot and the remaining deployment checks. A source check is not an end-to-end test of Discord, Telegram, music sites or your host.

## Privacy and upstream services

This repository is a configurable source distribution. It does not include a production database, personal saved-link collection, message archive, credentials, media library or existing Git history. Review local changes before committing them.

Third-party APIs, libraries and products remain the work of their respective maintainers. Review their terms and licenses before redistribution or deployment.
