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
    await message.reply("👋 හෙලෝ! Google Drive Link එකක් එවන්න. මම ඒ Video එක Telegram හරහා upload කරන්නම්.")

@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def download(client, message: Message):
    url = message.text.strip()
    if "drive.google.com" not in url:
        return await message.reply("❌ Valid Google Drive link එකක් නැහැ.")

    msg = await message.reply("📥 Downloading...")

    try:
        if "file/d/" in url:
            file_id = url.split("file/d/")[1].split("/")[0]
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            return await msg.edit("❌ Link එක format එක වැරදියි.")

        r = requests.get(direct_url, stream=True)
        filename = "gdrive_video.mp4"
        path = os.path.join(DOWNLOAD_DIR, filename)

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

        await msg.edit("✅ Download done. Uploading...")

        await client.send_video(
            chat_id=message.chat.id,
            video=path,
            caption="🎬 Here's your video!",
            supports_streaming=True
        )

        os.remove(path)
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

app.run()
