import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from urllib.parse import parse_qs, urlparse

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_file_id(url: str) -> str | None:
    if "drive.google.com" not in url:
        return None
    parsed = urlparse(url)
    if "/file/d/" in url:
        return url.split("/file/d/")[1].split("/")[0]
    elif "id=" in url:
        return parse_qs(parsed.query).get("id", [None])[0]
    return None

def get_filename_from_headers(headers):
    content_disposition = headers.get("Content-Disposition", "")
    match = re.search('filename="(.+?)"', content_disposition)
    return match.group(1) if match else "downloaded_file"

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 Send me a Google Drive link and I’ll download and upload the file here.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_drive_link(client, message: Message):
    url = message.text.strip()
    file_id = extract_file_id(url)

    if not file_id:
        return await message.reply("❌ Invalid Google Drive link.")

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    await message.reply("📥 Downloading from Google Drive...")

    try:
        response = requests.get(download_url, stream=True)
        if "text/html" in response.headers.get("Content-Type", ""):
            return await message.reply("⚠️ Cannot download. File might be private or too large for direct download.")

        filename = get_filename_from_headers(response.headers)
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        await message.reply_document(document=filepath, caption="📤 File uploaded successfully.")
        os.remove(filepath)

    except Exception as e:
        await message.reply(f"❌ Failed to process: {e}")

if __name__ == "__main__":
    print("✅ Bot Started and Running")
    app.run()
