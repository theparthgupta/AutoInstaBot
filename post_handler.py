import os
import threading
from instagrapi import Client
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
INSTAGRAM_USERNAME = os.environ.get("IG_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("IG_PASSWORD")


# login every time — not ideal but simplest for now
def login_instagram():
    cl = Client()
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    return cl


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def handle_post_reel(chat_id, video_url, caption=""):
    try:
        cl = login_instagram()

        # download video
        fname = "/tmp/reel_video.mp4"
        r = requests.get(video_url, stream=True, timeout=60)
        if r.status_code != 200:
            send_telegram_message(chat_id, "Failed to download video. Check the URL.")
            return

        with open(fname, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

        # upload as Reel
        cl.clip_upload(fname, caption)
        send_telegram_message(chat_id, "🎬 Reel posted successfully ✅")

    except Exception as e:
        print("reel post error:", e)
        send_telegram_message(chat_id, f"❌ Failed to post reel: {e}")


def handle_update(update_json):
    try:
        message = update_json.get("message") or update_json.get("edited_message")
        if not message:
            return

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if not text:
            return

        # Command: /reel <video_url> [optional caption]
        if text.startswith("/reel"):
            parts = text.split(maxsplit=2)
            if len(parts) < 2:
                send_telegram_message(chat_id, "Usage: /reel <video_url> [optional caption]")
                return

            video_url = parts[1]
            caption = parts[2] if len(parts) > 2 else ""

            send_telegram_message(chat_id, "Uploading your Reel 🎥...")
            threading.Thread(target=handle_post_reel, args=(chat_id, video_url, caption)).start()

    except Exception as e:
        print("handle_update error:", e)
