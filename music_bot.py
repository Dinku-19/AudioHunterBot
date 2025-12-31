import requests
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

SPOTIFY_API = "https://fast-dev-apis.vercel.app/spotify"


# ---------------- START COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Send me a song name.\n\nSupports:\n✔ Spotify\n✔ YouTube\n\nExample:\nAzul Guru Randhawa"
    )


# ---------------- SPOTIFY SEARCH ----------------
def search_spotify(query):
    try:
        res = requests.get(SPOTIFY_API, params={"q": query})
        data = res.json()
        return data if data.get("status") else None
    except:
        return None


# ---------------- YOUTUBE DOWNLOAD ----------------
def download_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "song.mp3",
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        title = info["entries"][0]["title"]
        artist = info["entries"][0]["uploader"]
        return "song.mp3", title, artist


# ---------------- HANDLE USER MESSAGE ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text("🔎 Searching...")

    # Try Spotify
    data = search_spotify(query)

    if data:
        title = data["title"]
        artist = data["artist"]
        audio_url = data["audio_url"]

        await update.message.reply_text("🎧 Found on Spotify ✔\nSending song...")

        audio_data = requests.get(audio_url).content

        await update.message.reply_audio(
            audio=audio_data,
            title=title,
            performer=artist
        )
        return

    # If Spotify fails → YouTube
    await update.message.reply_text("⚠️ Not found on Spotify\n🎥 Trying YouTube...")

    try:
        filename, title, artist = download_youtube(query)

        await update.message.reply_audio(
            audio=open(filename, "rb"),
            title=title,
            performer=artist
        )

    except Exception as e:
        await update.message.reply_text("❌ Failed to download song. Try another name.")


# ---------------- MAIN APP ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()






