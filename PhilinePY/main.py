import discord
from discord import *
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
import json
import aiohttp
from pyexpat.errors import messages
import random
import time
from discord.ui import Button, View

config = dotenv_values("PhilinePY/.env")
token = config['DISCORD_TOKEN']
server = config['RESPONSE_SERVER']

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user}.')
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} commands.')
            print(f'You can use the Bot now!')
        except Exception as e:
            print(f'Error syncing commands: {e}')

intents = Intents.default()
intents.message_content = True
intents.typing = True
intents.presences = True
intents.members = True

client = Client(command_prefix="$", intents=intents, activity=discord.Activity(name="/help", type=discord.ActivityType.listening))
active_threads = {}

emojis = ["<a:85336typing:1365047868116828302>", "<a:9754_Loading:1365047852740641025>", "<a:9628discordloading:1365047842674311319>", "<a:9520whiteheartsloading:1365047823673982976>", "<a:8299_Loading:1365047813011935325>", "<a:6767loading:1365047803478282331>", "<a:5564_Loading_Color:1365047789033099335>", "<a:5268_loading:1365047772327186645>", "<a:3859_Loading:1365047738672091287>", "<a:3339_loading:1365047721588817980>", "<a:3339_loading:1365047721588817980>", "<a:2923printsdark:1365047694548271245>", "<a:2908loading:1365047682296709130>", "<a:2259gearsloading:1365047670384758896>", "<a:1792loading:1365047660264034355>", "<a:1333loading:1365047651736752188>"]
random_emoji = random.choice(emojis)

class ThreadManagementView(View):
    def __init__(self, thread: discord.Thread):
        super().__init__()
        self.thread = thread

        self.delete_button = Button(style=discord.ButtonStyle.danger, label="Delete", emoji="<:14605delete:1364986521941315606>")
        self.delete_button.callback = self.button_delete_thread
        self.add_item(self.delete_button)

        self.private_button = Button(style=discord.ButtonStyle.secondary, label="Private", emoji="<:69921moderatorhexagon:1364986476655411301>")
        self.private_button.callback = self.button_private_thread
        self.add_item(self.private_button)

    async def button_delete_thread(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"> Deleting Thread {self.thread.mention} <a:loadingdotsline:1364568277799534592>")
        try:
            await self.thread.delete()
            await interaction.message.add_reaction("<a:check:1364986556456370227>")
            await interaction.message.add_reaction("<:7157deleteticket:1364986548499648592>")
            await interaction.edit_original_response(content=f"> Thread deleted! <a:check:1364986556456370227>")
        except discord.Forbidden:
            await interaction.response.send_message("Fehler: Ich habe keine Berechtigung, diesen Thread zu löschen.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ein unerwarteter Fehler ist aufgetreten: {e}", ephemeral=True)

    async def button_private_thread(self, interaction: discord.Interaction):
        await self.thread.edit(archived=True, auto_archive_duration=60, reason="Thread is now private.")
        await interaction.message.add_reaction("<a:check:1364986556456370227>")
        await interaction.message.add_reaction("<:69921moderatorhexagon:1364986476655411301>")
        await interaction.followup.send(f"> Thread is now private! ({self.thread.mention}) <a:check:1364986556456370227>")
@client.tree.command(name="setup", description="Setup the Bot")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="Setup", color=0xa020f0)
    embed.add_field(name="", value="Setup the Bot in the current channel. If you do, it can __only__ be used in this channel.", inline=False)
    embed.set_author(name="Phi-Trash - Setup")
    embed.set_footer(text="/help to see all commands!")
    
    async def button_callback(interaction: discord.Interaction):
        # Starting the setup process
        channel = interaction.channel
        legit = False
        for member in channel.members:
            if member.name == "nino.css":
                legit = True
                break
        if legit:
            await interaction.response.defer()
            initial_message = await interaction.followup.send(f"I'm setting up {channel.mention}! <a:loadingdotsline:1364568250700005376>", ephemeral=True)
            await client.change_presence(activity=discord.Activity(name=f"setting up {channel.name}", type=discord.ActivityType.competing))        

            CHANNEL_IDS = []
            CHANNEL_IDS.append(channel.id) 
            channels_to_save = {'saved_channel_id': CHANNEL_IDS}
            file_name = str(interaction.guild.id) + ".json"
            try:
                with open(file_name, "w") as f:
                    json.dump(channels_to_save, f, indent=4)
                print(f"Guild-IDs saved in '{file_name}'")
                
            except IOError as e:
                print(f"Error while writing file: '{file_name}': {e}")

            await interaction.followup.edit_message(initial_message.id, content=f"Setup completed! You can now use the Bot in {channel.mention} <a:Anime:1364571387620098048>")
            await client.change_presence(activity=discord.Activity(name=f"/help", type=discord.ActivityType.listening))
            await interaction.followup.send(f"## > This Channel is now the Channel for PHI. Use `/help` to get a help menu. ", ephemeral=False)
        else:
            await interaction.response.send_message("Owner is not in this channel, couldn't start the setup.", ephemeral=True)
            
    s_button = Button(style=discord.ButtonStyle.primary, label="Setup this channel", emoji="<:setup:1364726566155718678>")
    s_button.callback = button_callback

    view = View()
    view.add_item(s_button)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
@client.tree.command(name="help", description="Get a help menu!")
async def help(interaction: discord.Interaction):

        embed = discord.Embed(title= random_emoji + "  Help", description="This is a list of commands from this bot!", color=0xa020f0)
        embed.add_field(name="", value="**Commands:**", inline=False)
        embed.add_field(name="/setup", value="Setup the Bot in this channel!", inline=False)
        embed.add_field(name="/ask", value="Get started with chatting!", inline=False)
        embed.add_field(name="", value="You have to choose a Model from this list:\n > **phi4** *(slower, by Microsoft)* \n > **gemma3** *(medium, by Google)* \n > **deepseek-r1** *(faster, by Deepseek)* \n > **qwen2** *(faster, by Alibaba)* \n > **llama3.2** *(slower, by Meta)*", inline=True)
        embed.add_field(name="/help", value="Get this help menu!", inline=False)
        embed.set_footer(text="go to our Github to see the code! (It's open source!)")
        embed.add_field(name="Github", value="<:Github:1364634620393422968> [Github repo](https://github.com/nino749/Philine)", inline=False)
        embed.set_author(name="© 2025 Philine - nino.css (Python) | game.crash (Javascript)")
        
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)
@client.tree.command(name="ask", description="Ask something to Phi!")
@app_commands.choices(model=[
    app_commands.Choice(name="phi4 (slower)", value="phi4-mini:latest"),
    app_commands.Choice(name="gemma3 (faster)", value="gemma3:1b"),
    app_commands.Choice(name="deepseek-r1 (faster)", value="deepseek-r1:1.5b"),
    app_commands.Choice(name="qwen2 (medium)", value="qwen2:1.5b"),
    app_commands.Choice(name="llama3.2 (slower)", value="llama3.2:3b"),
])
@app_commands.describe(model="Choose a model to use")
async def ask(interaction: discord.Interaction, model: app_commands.Choice[str]):
    file_name = str(interaction.guild.id) + ".json"
    channel_id = None
    try:
        with open(file_name, "r") as f:
            channels_to_load = json.load(f)
            loaded_channel_id = channels_to_load.get('saved_channel_id', [])
            channel_id = loaded_channel_id[0] if loaded_channel_id else None
    except IOError as e:
        print(f"Fehler beim Laden der Datei '{file_name}': {e}")
    if interaction.channel.id == channel_id:
        await interaction.response.send_message("> Sending  "+ "<a:Anime:1364571387620098048>")

        thread = await interaction.channel.create_thread(name=f"Chat by {interaction.user.name}", type=discord.ChannelType.public_thread)
        thread_management_view = ThreadManagementView(thread)

        await client.change_presence(activity=discord.Activity(name=f"setting up {model.value}", type=discord.ActivityType.competing))

        thread_embed = discord.Embed(
            title="Thread created! <a:check:1364986556456370227>",
            description=f"** > {interaction.user.mention} Created new Thread for you, have fun! <a:Anime:1364571387620098048>**",
            color=0xa020f0
        )
        thread_embed.add_field(name="Thread ID", value=f"{thread.id}", inline=True)
        thread_embed.add_field(name="Channel ID", value=f"{interaction.channel.id}", inline=True)
        thread_embed.add_field(name="User ID", value=f"{interaction.user.id}", inline=True)
        thread_embed.set_footer(text="Just chat with the Bot, you dont have to use /ask anymore.")
        thread_embed.set_author(name=f"You're chatting with: {model.value}")
        thread_embed.timestamp = discord.utils.utcnow()

        await thread.send(view=thread_management_view, embed=thread_embed)

        active_threads[thread.id] = {
            "model": model.value,
            "user_id": interaction.user.id,
            "last_message": ""
        }

        embed = discord.Embed(
            title="Thread created!",
            description=f"** > {interaction.user.mention} Created new Thread for you: {thread.mention}, have fun! <a:Anime:1364571387620098048>**",
            color=0xa020f0
        )
        embed.add_field(name="Thread ID", value=f"{thread.id}", inline=True)
        embed.add_field(name="Channel ID", value=f"{interaction.channel.id}", inline=True)
        embed.add_field(name="User ID", value=f"{interaction.user.id}", inline=True)
        embed.set_footer(text="You can use the Bot now!")
        embed.set_author(name="Phi-Trash - Thread created!")
        embed.timestamp = discord.utils.utcnow()

        await interaction.edit_original_response(view=thread_management_view, embed=embed, content="")
        await client.change_presence(activity=discord.Activity(name=f"finished!", type=discord.ActivityType.competing))
        time.sleep(5)
        await client.change_presence(activity=discord.Activity(name=f"/help", type=discord.ActivityType.listening))

    else:
        await interaction.response.send_message("You can't use the Bot in this channel. Please use the setup command to set up the Bot in this channel.", ephemeral=True)
async def send_ai_answer(thread, model, question, thinking_message):
    try:
        start_time = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            url = server
            data = {
                "model": model,
                "messages": [{"role": "user", "content": question}],
                "stream": False,
                "options": {
                    "temperature": 0.9, 
                    "mirostat": 2
                    }
            }
            active_threads[thread.id]["last_message"] = question
            
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    ai_msg = (await response.content.read()).splitlines()
                    response_data = ""

                    for line in ai_msg:
                        try:
                            a = json.loads(line).get("message")
                            if a:
                                response_data += a.get("content", "")
                        except Exception:
                            continue
                        
                    def count_words(response_data):    
                        letters = response_data.split()
                        return len(letters)
                
                    end_time = time.perf_counter()
                    latency = (end_time - start_time)

                    parts = [response_data[i:i+1900] for i in range(0, len(response_data), 1900)]

                    r_button = Button(style=discord.ButtonStyle.primary, label="reroll", emoji="<:setup:1364726566155718678>")
                    r_button.callback = on_reroll
                    view = View()
                    view.add_item(r_button)
                    
                    embed = discord.Embed(
                        title="Stats of this reply",
                        color=0xa020f0
                    )
                    
                    embed.add_field(name="Model", value=f"{model}", inline=True)
                    embed.add_field(name="Latency", value=f"{round(latency)}s or {round(latency *1000)}ms", inline=True)
                    embed.add_field(name="Words", value=f"{count_words(response_data)}", inline=True)
                    
                    await thinking_message.edit(view=view, embed=embed, content=parts[0])
                    for part in parts[1:]:
                        await thread.send(part)
                    
    except Exception as e:
            await thread.send(content=f'> <:Pepecry:1364571373912985622> An error occurred: {e} <:Pepecry:1364571373912985622>')
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.Thread):
        thread = message.channel

        if thread.id in active_threads:
            thread_info = active_threads[thread.id]
            model = thread_info["model"]
            
        thinking_message = await thread.send(content=f"> {model} is Thinking {random_emoji}")
        
        await send_ai_answer(thread, model, message.content, thinking_message)
        
    await client.process_commands(message)   
    
async def on_reroll(interaction: discord.Interaction):
    if isinstance(interaction.channel, discord.Thread):
        thread = interaction.channel
        await interaction.response.defer()
        
        await interaction.message.delete()
        
        if thread.id in active_threads:
            thread_info = active_threads[thread.id]
            model_name = thread_info["model"]
            active_messages = thread_info["last_message"]
            
        thinking_message = await thread.send(content=f"> Thinking {random_emoji}")
        print(f"Rerolling for thread {thread.id} with model {model_name} and message {active_messages}")
        await send_ai_answer(thread, model_name, active_messages, thinking_message)    
client.run(token)