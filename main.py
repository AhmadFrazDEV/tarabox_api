from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

@app.route('/extract')
def extract_video():
    url = request.args.get('link')
    if not url:
        return jsonify({"error": "No link provided"}), 400

    video_url = ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            def is_valid_video_url(link):
                return (
                    re.search(r"(\.mp4|\.m3u8|\.ts)(\?|$)", link) and
                    "google" not in link and
                    "analytics" not in link and
                    "ads" not in link and
                    "collect" not in link
                )

            def handle_request(request):
                nonlocal video_url
                req_url = request.url
                if is_valid_video_url(req_url):
                    print("🎯 Found video:", req_url)
                    video_url = req_url

            page.on("request", handle_request)
            page.goto(url)
            page.wait_for_timeout(20000)  # Wait 20 seconds

            browser.close()

            if video_url:
                return jsonify({"video_url": video_url})
            else:
                return jsonify({"error": "No video stream found"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)