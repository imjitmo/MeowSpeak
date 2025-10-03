import os
import discord
from discord.ext import commands
from gtts import gTTS

TOKEN = os.environ["DISCORD_TOKEN"]  # replace with your token directly for now

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TEXT_CHANNEL_ID = 1423696468497141800  # replace with your text channel ID

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"DEBUG: Got message in {message.channel.id}: {message.content}")

    if message.channel.id != TEXT_CHANNEL_ID:
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

    await bot.process_commands(message)

bot.run(TOKEN)
