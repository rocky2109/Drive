import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 මට Google Drive link එකක් එවන්න. මම file එක Telegram වලට upload කරන්නම්.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_gdrive(client, message: Message):
    url = message.text.strip()
    if "drive.google.com" not in url:
        return await message.reply("❌ මෙය valid Google Drive link එකක් නොවෙයි.")

    await message.reply("📥 Downloading...")

    # Convert standard drive link to direct-download link
    try:
        file_id = url.split("/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    except:
        return await message.reply("❗ Link එක invalid බව පෙනේ.")

    try:
        response = requests.get(download_url, stream=True)
        cd = response.headers.get("Content-Disposition", "")
        filename = "file.mp4"
        if "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                f.write(chunk)

        await message.reply_document(document=filepath, caption="📤 File uploaded ✅")
        os.remove(filepath)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

if __name__ == "__main__":
    print("✅ Bot Started")
    app.run()
