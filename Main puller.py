#This script will pull all images from a discord channel and save them to a specified folder.

import discord
import os
import aiohttp
from urllib.parse import urlparse


## CHANGE THESE VALUES ##
# Replace with your bot token, channel ID, and download folder
TOKEN = 'YOUR TOKEN HERE'
CHANNEL_ID = 1234567890  # Replace with your channel's ID
DOWNLOAD_FOLDER = 'YOUR DIRECTORY HERE'  # Modify as needed


####################################################################################################################################
#######################       D O  N O T  C H A N G E ! !    #######################################################################
####################################################################################################################################
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    channel = await client.fetch_channel(CHANNEL_ID)  # Ensures correct channel fetching
    image_files = []  # List to store image URLs

    async for message in channel.history(limit=None):  # Fetch all messages
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                image_files.append(attachment.url)  # Store URLs for counting

    total_images = len(image_files)  # Total images to download
    if total_images == 0:
        print("No images found.")
        await client.close()
        return

    # Download images with a progress counter
    for idx, image_url in enumerate(image_files, start=1):
        parsed_url = urlparse(image_url)  # Parse the URL
        filename = os.path.basename(parsed_url.path)  # Get the filename without query parameters
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)  # Full path for saving

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await resp.read())
                    print(f"Image {idx} out of {total_images} finished downloading.")

    print("All images downloaded successfully.")
    await client.close()

client.run(TOKEN)

####################################################################################################################################
#######################       D O  N O T  C H A N G E ! !    #######################################################################
####################################################################################################################################