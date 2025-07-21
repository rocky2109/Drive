# main.py
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("👋 හෙලෝ! Google Drive Video link එකක් එවන්න.")

@app.on_message(filters.text & filters.private)
async def download_file(client, message: Message):
    url = message.text.strip()
    if "drive.google.com" not in url:
        return await message.reply_text("❌ මේක valid Google Drive link එකක් නෙමෙයි.")

    await message.reply_text("📥 Downloading...")

    # Google Drive direct download link generate කරලා දාන්න (file ID එකෙන්)
    file_id = url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(download_url, stream=True)
    filename = f"video.mp4"
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1048576):
            if chunk:
                f.write(chunk)

    await client.send_document(message.chat.id, filename, caption="📦 File uploaded!")
    os.remove(filename)

app.run()

