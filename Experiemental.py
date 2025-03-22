import discord
import os
import aiohttp
import asyncio
import logging
from discord import app_commands
from urllib.parse import urlparse
from image_utils import zip_images, unzip_images
from cloudflare_buster import download_image_with_browser

# ====== Configuration ======
TOKEN = 'YOURTOKENHERE'
GUILD_ID = 1234567890  # server ID
DOWNLOAD_FOLDER = 'downloaded'


# ====== Logging Setup ======
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

# ====== Discord Bot Setup ======
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

# ====== /download_images ======
@client.tree.command(name="download_images", description="Download images from a channel and zip them.")
@app_commands.describe(channel="The channel to download images from")
async def download_images(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.send_message("\U0001F4E5 Scanning messages for images...", ephemeral=True)
    try:
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        image_urls = []
        async for message in channel.history(limit=None):
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    image_urls.append((attachment.url, attachment.filename))

        total = len(image_urls)
        if total == 0:
            await interaction.followup.send("\u274C No images found to download.")
            return

        message = await interaction.followup.send(f"\U0001F4E5 Downloading 0 of {total} images...", wait=True)
        image_paths = []

        for idx, (url, filename) in enumerate(image_urls, start=1):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            downloaded = False

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
                }

                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url) as resp:
                        content_type = resp.headers.get('Content-Type', '')

                        if resp.status == 200 and content_type.startswith('image/'):
                            with open(file_path, 'wb') as f:
                                f.write(await resp.read())
                            downloaded = True
                            image_paths.append(file_path)
                        else:
                            logging.warning(f"Blocked or invalid content-type: {content_type} from {url}")
                            raise Exception("Not an image")

            except Exception as e:
                logging.warning(f"Aiohttp failed. Using Playwright for: {url}")
                success = await download_image_with_browser(url, file_path)
                if success:
                    image_paths.append(file_path)
                    downloaded = True
                    logging.info(f"✅ Downloaded with Playwright: {filename}")
                else:
                    logging.error(f"❌ Failed to download image: {filename} from {url}")

            await message.edit(content=f"\U0001F4E5 Downloading image {idx} of {total}... {'✅' if downloaded else '❌'}")

        zip_path = zip_images(image_paths, DOWNLOAD_FOLDER, "images_downloaded.zip")
        await message.edit(content="✅ Download complete. Uploading zip file...")
        await interaction.followup.send(file=discord.File(zip_path))
        logging.info(f"Downloaded {total} images from #{channel.name}")

    except Exception as e:
        logging.error(f"Error during download: {e}")
        await interaction.followup.send(f"\u274C Error downloading images: {e}")

# ====== /upload_images ======
@client.tree.command(name="upload_images", description="Upload zipped images to a channel")
@app_commands.describe(channel="The channel to upload images to", zip_name="The name of the zip file in 'downloaded/'")
async def upload_images(interaction: discord.Interaction, channel: discord.TextChannel, zip_name: str):
    await interaction.response.send_message("\U0001F4E4 Preparing upload...", ephemeral=True)
    try:
        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)
        if not os.path.exists(zip_path):
            await interaction.followup.send("\u274C Zip file not found.")
            return

        extract_dir = unzip_images(zip_path)
        image_files = [f for f in os.listdir(extract_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

        if not image_files:
            await interaction.followup.send("\u274C No images found in zip file.")
            return

        total = len(image_files)
        message = await interaction.followup.send(f"\U0001F4E4 Uploading 0 of {total} images...", wait=True)

        for idx, image in enumerate(image_files, start=1):
            file_path = os.path.join(extract_dir, image)
            with open(file_path, 'rb') as f:
                await channel.send(file=discord.File(f))
            await message.edit(content=f"\U0001F4E4 Uploading image {idx} of {total}...")
            await asyncio.sleep(1)

        await message.edit(content=f"✅ Upload complete. {total} images sent to #{channel.name}.")
        logging.info(f"Uploaded {total} images to #{channel.name}")

    except Exception as e:
        logging.error(f"Error during upload: {e}")
        await interaction.followup.send(f"\u274C Error uploading images: {e}")

client.run(TOKEN)
