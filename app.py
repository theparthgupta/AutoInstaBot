from flask import Flask, request, jsonify
import os
from post_handler import handle_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json(force=True)
        # delegate heavy logic to post_handler
        handle_update(update)
        return jsonify({"ok": True})
    except Exception as e:
        # log for debugging
        print("webhook error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    # debug server for local testing only
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
