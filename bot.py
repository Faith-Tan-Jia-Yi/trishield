import discord
import responses
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import ui


# Modal Wrapper
class PopUp(ui.Modal, title = "Trishield Intervention"):
    def __init__(self, message:str, response:str) -> None:
        super().__init__()
        label = response
        self.answer = ui.TextInput(label= label, style= discord.TextStyle.paragraph, default= message, max_length= 4000)
        self.add_item(self.answer)

    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        # Extracts user response on Modal
        message = self.children[0].value

        # Sets censor to true if the message is still offensive
        censor = True
        if responses.handle_response(message) == None:
            censor = False
        
        # Creates embed in channel
        await create_embed(message, censor, interaction)

async def create_embed(message:str, censor:bool, interaction: discord.Interaction):
    embed = discord.Embed()

    # Hides text if censor is true and adds a trigger warning
    if (censor):
        embed.description = "||"+message+"||"
        embed.set_footer(text="Trigger Warning")
    else:
        embed.description = message
    
    # Sets author as the user
    embed.set_author(name= interaction.user.display_name, icon_url= interaction.user.display_avatar)
    await interaction.response.send_message(embed= embed)


def run_discord_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="!", intents=intents)

    # On start, when bot is connected this will print
    @client.event
    async def on_ready():
        synced = await client.tree.sync()
        print("Synced "+ str(len(synced)) +" commands.")
        print(f"{client.user} is now running!")


    @client.tree.command(name= "clear")
    async def clear(interaction: discord.Interaction):
        await interaction.channel.purge()
    
    # Returns the controller applet
    @client.tree.command(name= "t", description="Send a text to a Trishield protected channel")
    async def controller(interaction: discord.Interaction, message: str):
        # Send the message to the handler to check for toxicity
        response = responses.handle_response(message)

        # Triggers modal if the message is offensive. Otherwise creates embed in channel
        if response == None:
            await create_embed(message=message, censor=False, interaction= interaction)
        else:
            await interaction.response.send_modal(PopUp(message= message, response= response))
        
    
    # Does not allow users to send messages in the chat
    @client.event
    async def on_message(message):
        # Checks if the author is the bot
        if message.author == client.user:
            return

        # Extracts message information
        username = message.author
        user_message = message.content
        channel = message.channel

        # Deletes message
        await message.delete()
        # Sends a self-destructing information message
        await channel.send("You can only send messages with /t", delete_after= 5)
        # print(f"{str(username)} said {str(user_message)} in {str(channel)}") 

    client.run(TOKEN)
