from datetime import datetime
import discord
import os
import speech2text
from dotenv import load_dotenv

load_dotenv()
token = str(os.getenv("TOKEN"))
bot = discord.Bot()
connections = {}

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and member.guild.id in connections and after.channel is None:
        vc = connections[member.guild.id]
        vc.stop_recording()

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

    recordDatetime = datetime.now()
    vc.start_recording(
        discord.sinks.MP3Sink(),
        stop_callback,
        ctx.channel,
        recordDatetime
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

async def stop_callback(sink: discord.sinks, channel: discord.TextChannel, recordTimestamp: datetime):
    await sink.vc.disconnect()

    timestamp = datetime.now().strftime("%d-%m-%Y %H%M%S")
    dir = os.path.join("output", timestamp)
    os.mkdir(dir)

    userTranscripts = {}

    for user_id, audio in sink.audio_data.items():
        file = os.path.join(dir, f"{user_id}.{sink.encoding}")
        with open(file, "wb") as f:
            f.write(audio.file.getbuffer())
        user = channel.guild.get_member(user_id)
        userTranscripts.update(speech2text.get_user_transcript(recordTimestamp, user.display_name, file))

    if len(userTranscripts):
        speech2text.compile_user_transcript(sorted(userTranscripts.items()), dir)
        file = discord.File(os.path.join(dir, "transcript.txt"), f"{dir}.txt")
        await channel.send(f"Finished stalking!", file=file)

bot.run(token)
