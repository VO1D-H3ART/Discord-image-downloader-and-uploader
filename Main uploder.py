#this code is used to upload images to a discord channel

import discord
import os
import asyncio

## CHANGE THESE VALUES ##
# Replace with your bot token, channel ID, and download folder
TOKEN = 'YOUR TOKEN HERE'
CHANNEL_ID = 1234567890  # Replace with your channel's ID
DOWNLOAD_FOLDER = 'YOUR DIRECTORY HERE'  # Modify as needed


####################################################################################################################################
#######################       D O  N O T  C H A N G E ! !    #######################################################################
####################################################################################################################################

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Error: Invalid channel ID or bot lacks permission to send messages.")
        await client.close()
        return

    # Get all image files in the folder
    image_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

    total_images = len(image_files)
    if total_images == 0:
        print("No images found to upload.")
        await client.close()
        return

    # Upload images one by one with progress counter
    for idx, image in enumerate(image_files, start=1):
        file_path = os.path.join(UPLOAD_FOLDER, image)

        try:
            with open(file_path, 'rb') as f:
                await channel.send(file=discord.File(f))
            print(f"Uploaded {idx} out of {total_images}: {image}")
        except Exception as e:
            print(f"Failed to upload {image}: {e}")

        await asyncio.sleep(1)  # Delay to avoid hitting rate limits

    print("All images uploaded successfully.")
    await client.close()

client.run(TOKEN)



####################################################################################################################################
#######################       D O  N O T  C H A N G E ! !    #######################################################################
####################################################################################################################################
