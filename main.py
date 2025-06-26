
from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import re
import os

app = Flask(__name__)

# 🔗 Terabox link (you can replace it or later take as input)
TERABOX_LINK = "https://1024terabox.com/s/1nCEAPmKnGU6VbTotuHagoQ"

@app.route('/')
def fetch_video():
    video_url = ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            def is_valid_video_url(link):
                return (
                    re.search(r"(\.mp4|\.m3u8|\.ts)(\?|$)", link)
                    and "google" not in link
                    and "analytics" not in link
                    and "ads" not in link
                    and "collect" not in link
                )

            def handle_request(request):
                nonlocal video_url
                req_url = request.url
                if is_valid_video_url(req_url):
                    print("🎯 Found video:", req_url)
                    video_url = req_url

            page.on("request", handle_request)
            page.goto(TERABOX_LINK)
            page.wait_for_timeout(20000)  # Wait 20 seconds
            browser.close()

            if video_url:
                return jsonify({"video_url": video_url})
            else:
                return jsonify({"error": "No video stream found"})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Flask binding for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
