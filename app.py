import os
import requests
import yt_dlp
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from instagrapi import Client

# ================= Flask Web Server for Uptime =================
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "✅ Bot is running!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

# =============================================================================

# ================= Instagram Client Setup =================
INSTAGRAM_USERNAME = os.environ.get("IG_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("IG_PASSWORD")

cl = Client()
cl.load_settings("session.json")  # Load your saved login session
cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
print(f"✅ Logged in as @{INSTAGRAM_USERNAME}")

# =============================================================================

# ================= Telegram Bot Setup =================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

def download_reel(url):
    """Download reel video using yt-dlp."""
    os.makedirs("downloads", exist_ok=True)
    output_path = os.path.join("downloads", "reel.mp4")
    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send me a public Instagram reel link and I’ll repost it to your account!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com/reel/" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram reel URL.")
        return

    await update.message.reply_text("📥 Downloading your reel...")

    try:
        video_path = download_reel(url)
        await update.message.reply_text("📤 Uploading to Instagram...")

        caption = "#reels #viral #trending #explorepage"
        cl.clip_upload(video_path, caption=caption)

        await update.message.reply_text("✅ Reel uploaded successfully!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

    finally:
        if os.path.exists("downloads/reel.mp4"):
            os.remove("downloads/reel.mp4")
            print("🧹 Deleted temporary file.")

# =============================================================================

# ================= Start Servers =================
def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is live! Send a reel link to upload.")
    app.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    start_bot()
