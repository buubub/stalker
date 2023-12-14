import discord
import os
from dotenv import load_dotenv

load_dotenv()
token = str(os.getenv("TOKEN"))
bot = discord.Bot()
connections = {}

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(description = "Ping")
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.respond(f"Pong! Latency is {int(latency)}ms")

@bot.slash_command(description = "Stalk a Voice Channel")
async def stalk(ctx):
    voice  = ctx.author.voice
    if not voice:
        return await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        discord.sinks.WaveSink(),
        stop_callback,
        ctx.channel
    )
    await ctx.respond("Started stalking. .")

@bot.slash_command(description = "Stop Stalking")
async def stop(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
        await vc.disconnect()
        await ctx.respond("Stopped stalking. .")
    else:
        await ctx.respond("I am currently not stalking!")

async def stop_callback(sink: discord.sinks, channel: discord.TextChannel, *args):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)

bot.run(token)
