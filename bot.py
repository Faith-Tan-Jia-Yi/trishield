import discord
import responses
import os
from dotenv import load_dotenv
from googleapiclient import discovery
import json


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # setting up perspective api client
    PERSPECTIVE = os.getenv('PERSPECTIVE_TOKEN')
    global apiclient
    apiclient = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=PERSPECTIVE,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    )
    # threshold for toxicity can be defined in .env file
    global threshold
    threshold = os.getenv('TOXICITY_THRESHOLD')

        # On start, when bot is connected this will print
    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        # Checks if the author is the bot
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said {user_message} in {channel}")

        # Send message privately to user
        if user_message[0] == "?":
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)