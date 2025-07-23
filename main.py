import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_API_KEY = os.getenv("GDRIVE_API_KEY")

app = Client("gdrive_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 Send a Google Drive file or folder link. I'll download and upload it here.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_gdrive(client, message: Message):
    url = message.text.strip()

    if "drive.google.com" not in url:
        return await message.reply("❌ Invalid Google Drive link.")

    await message.reply("📥 Processing...")

    # Check if it's a folder link
    if "/folders/" in url:
        folder_id = url.split("/folders/")[1].split("?")[0]
        api_url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&key={GDRIVE_API_KEY}&fields=files(id,name,mimeType)"

        try:
            res = requests.get(api_url)
            files = res.json().get("files", [])

            if not files:
                return await message.reply("📁 Folder is empty or private.")

            for file in files[:5]:  # limit to 5 files to avoid flooding
                file_id = file["id"]
                name = file["name"]
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                filepath = os.path.join(DOWNLOAD_DIR, name)

                r = requests.get(download_url, stream=True)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)

                await message.reply_document(document=filepath, caption=f"📤 Uploaded: `{name}`")
                os.remove(filepath)

        except Exception as e:
            await message.reply(f"❌ Error: {e}")

    elif "/file/d/" in url:
        try:
            file_id = url.split("/file/d/")[1].split("/")[0]
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = requests.get(download_url, stream=True)
            cd = response.headers.get("Content-Disposition", "")
            filename = "file.mp4"
            if "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('"')
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)

            await message.reply_document(document=filepath, caption="📤 File uploaded ✅")
            os.remove(filepath)

        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ Unsupported Google Drive link format.")

if __name__ == "__main__":
    print("✅ Bot Started")
    app.run()
