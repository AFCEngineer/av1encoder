import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from ffmpeg_utils import compress_video_av1

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

app = Client(
    "av1_compress_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "🔄 AV1 Compression Bot\n\n"
        "Send me a video file to compress it using AV1 encoding.\n\n"
        "⚙️ Compression Settings:\n"
        "- Video: SVT-AV1 (CRF 30)\n"
        "- Audio: Opus (128kbps)\n\n"
        "⚠️ Note: AV1 encoding is CPU-intensive and may take time."
    )

@app.on_message(filters.video | filters.document)
async def handle_video(client: Client, message: Message):
    # Check if user is owner if OWNER_ID is set
    if OWNER_ID and message.from_user.id != OWNER_ID:
        await message.reply_text("❌ This bot is private.")
        return

    try:
        status_msg = await message.reply_text("📥 Downloading video...")
        
        # Download video
        video_path = await message.download()
        
        await status_msg.edit_text("⏳ Compressing with AV1... (This may take a while)")
        
        # Compress video
        output_path = await compress_video_av1(video_path)
        
        if not output_path:
            await status_msg.edit_text("❌ Compression failed")
            return
            
        # Send compressed video
        await status_msg.edit_text("📤 Uploading compressed video...")
        await message.reply_video(
            video=output_path,
            caption=f"✅ Compressed with AV1\nOriginal: {os.path.getsize(video_path)//1024}KB\n"
                   f"Compressed: {os.path.getsize(output_path)//1024}KB"
        )
        
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await message.reply_text(f"❌ Error: {e}")
    
    finally:
        # Clean up files
        for file in [video_path, output_path]:
            try:
                if file and os.path.exists(file):
                    os.remove(file)
            except:
                pass

if __name__ == "__main__":
    logger.info("Starting AV1 Compression Bot...")
    app.run()
