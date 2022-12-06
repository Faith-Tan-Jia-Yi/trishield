import discord
import responses
import os
from dotenv import load_dotenv
from googleapiclient import discovery
import json
from discord.ext import commands
from discord import ui, ButtonStyle


def run_discord_bot():
    # Initializes Bot
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="!", intents=intents)

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

    # Bot Memory
    last_deleted_messages = {}
    last_bot_response = {}


    # View Wrapper
    class ButtonMenu(ui.View):
        def __init__(self, message:str, feedback:str):
            super().__init__()
            self.value = None
            self.message = message
            self.feedback = feedback
        
        # Pops modal so user can retype message
        @ui.button(label= "Edit Message", style=ButtonStyle.green)
        async def menuButton1(self, interaction: discord.Interaction, button: ui.Button):
            await interaction.response.send_modal(PopUp(self.message, self.feedback))
        
        # Posts (embedded) user comment 
        @ui.button(label= "Send Anyway", style=ButtonStyle.blurple)
        async def menuButton2(self, interaction: discord.Interaction, button: ui.Button):
            embed = discord.Embed()
            embed.description = "||"+self.message+"||"
            embed.set_footer(text="Trigger Warning")
            embed.set_author(name= interaction.user.display_name, icon_url= interaction.user.display_avatar)
            await interaction.response.send_message(embed= embed)


    # Modal Wrapper
    class PopUp(ui.Modal, title = "Trishield Intervention"):
        def __init__(self, message:str, response:str) -> None:
            super().__init__()
            
            # Frame modal
            label = response
            self.answer = ui.TextInput(label= label, style= discord.TextStyle.paragraph, default= message, max_length= 4000)
            self.add_item(self.answer)

        
        async def on_submit(self, interaction: discord.Interaction) -> None:
            # Extracts user response on Modal
            message = self.children[0].value
            response = responses.handle_response(message)
            embed = discord.Embed()
            
            # Bot sends ephemeral messages depending on toxicity
            # if it is non toxic, the bot asks the user to copy their message in chat
            # otherwise the bot explains the problem to the user and gives them a ButtonMenu
            if response == None:
                embed.title = "You're good to go!"
                embed.description = message
                embed.set_footer(text= "You can send this message in the channel")
                await interaction.response.send_message(embed= embed, ephemeral= True, delete_after=30)
            else:
                embed.title = "Trishield Alert!"
                embed.description = "Your message was flagged by Trishield"
                embed.add_field(name= "Message", value= message)
                embed.add_field(name= "Response", value= response)
                await interaction.response.send_message(view= ButtonMenu(message, response), embed= embed, ephemeral= True, delete_after= 30)
            

    

        # On start, when bot is connected this will print
    @client.event
    async def on_ready():
        synced = await client.tree.sync()
        print("Synced "+ str(len(synced)) +" commands.")
        print(f"{client.user} is now running!")

    # Allows channel to be cleaned. Will be removed later
    @client.tree.command(name= "clear")
    async def clear(interaction: discord.Interaction):
        await interaction.channel.purge(limit= 15)
    
    # Returns the controller applet
    @client.tree.command(name= "t", description="Send a text to a Trishield protected channel")
    async def controller(interaction: discord.Interaction):
        # Extract user id
        user_id = interaction.user.id
        # Pop modal with the deleted message prefilled
        message, response = query_memory(user_id)
        modal = PopUp(message, response)
        await interaction.response.send_modal(modal)
        
    def query_memory(user_id:int):
        # Query memory
        message = ""
        response = "Please write your message here"
        if user_id in last_deleted_messages.keys():
            message = last_deleted_messages[user_id]
            response = last_bot_response[user_id]
            last_deleted_messages.pop(user_id)
            last_bot_response.pop(user_id)
        return (message,response)
    # Everytime a new message is sent
    @client.event
    async def on_message(message):
        # Checks if the author is the bot
        if message.author == client.user:
            return

        # Extracts message information
        user_id = message.author.id
        user_message = message.content
        channel = message.channel

        response = responses.handle_response(user_message)
        print(response)
        
        if response != None:
            # Saves latest message
            last_deleted_messages[user_id] = user_message
            last_bot_response[user_id] = response
            # Deletes message
            await message.delete()
            # Sends a self-destructing information message
            await channel.send("You can only send messages with /t", delete_after= 5)


    client.run(TOKEN)