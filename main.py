import os
import discord
from discord.ext import commands, tasks
from gtts import gTTS
import asyncio

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TEXT_CHANNEL_ID = os.environ["CHANNEL_ID"]  # replace with your text channel ID
TEXT_CHANNEL_ID_2 = os.environ["CHANNEL_ID_2"]

# Track last activity per guild
last_activity = {}

# Timeout in seconds (15 minutes = 900 seconds)
IDLE_TIMEOUT = 15 * 60


@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    check_timeout.start()


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"DEBUG: Got message in {message.channel.id}: {message.content}")

    if message.channel.id != TEXT_CHANNEL_ID  and message.channel.id != TEXT_CHANNEL_ID_2:
        return

    if message.author.voice and message.author.voice.channel:
        voice_channel = message.author.voice.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)

        if not voice_client or not voice_client.is_connected():
            print("DEBUG: Connecting to voice...")
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            print("DEBUG: Moving to voice...")
            await voice_client.move_to(voice_channel)

        # Convert to speech
        tts = gTTS(text=message.content, lang="tl")
        temp_path = "tts.mp3"
        tts.save(temp_path)

        if not voice_client.is_playing():
            print("DEBUG: Playing TTS...")
            audio = discord.FFmpegPCMAudio(temp_path)
            voice_client.play(audio, after=lambda e: print("TTS finished:", e))

        # Update last activity timestamp
        last_activity[message.guild.id] = asyncio.get_event_loop().time()

    await bot.process_commands(message)


@tasks.loop(seconds=60)
async def check_timeout():
    """Disconnect the bot if idle for more than IDLE_TIMEOUT."""
    now = asyncio.get_event_loop().time()
    for guild_id, last_time in list(last_activity.items()):
        if now - last_time > IDLE_TIMEOUT:
            guild = bot.get_guild(guild_id)
            if guild and guild.voice_client:
                print(f"⏳ Timeout reached, disconnecting from {guild.name}")
                await guild.voice_client.disconnect()
                last_activity.pop(guild_id, None)


bot.run(TOKEN)
