# -*- coding: utf-8 -*-
import asyncio

import discord
from discord.ext import commands
from loguru import logger
from src.utils import add_track_queue, check_connection, LazyDict, play, skip_queue


TOKEN = ""  # bot's token
download_path = "./audio"
max_queue_size = 30  # max number of tracks in queue
command_prefix = "/"
messages = LazyDict(
    {
        "not_in_voice_channel": "",
        "user_not_in_voice_channel": "",
        "unsupported_url": "",
        "queue_full": "",
        "start_playing": "",
        "move_to_another_channel": "",
    }
)

headers = {"accept": "application/json", "Content-Type": "application/json"}


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True


bot = commands.Bot(command_prefix=command_prefix, intents=intents)

q = asyncio.Queue(maxsize=max_queue_size)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command(name="play")
async def add_track(ctx, *, user_input: str):
    await add_track_queue(ctx, user_input, download_path, q, messages)


@bot.command(name="skip-play")
async def skip_add_track(ctx, *, user_input: str):
    await skip_queue(ctx, messages)
    await add_track_queue(ctx, user_input, download_path, q, messages)


@bot.command(name="skip")
async def skip(ctx):
    await skip_queue(ctx, messages)


@bot.command(name="skip-all")
async def skip_all(ctx):
    vc, is_connected, is_in_same_channel = check_connection(ctx)
    if not is_connected:
        await ctx.send(messages["not_in_voice_channel"])
    else:
        if vc.is_playing() or vc.is_paused():
            while not q.empty():
                q.get_nowait()
            vc.stop()
            await vc.disconnect()


@bot.command(name="pause")
async def pause(ctx):
    vc, is_connected, is_in_same_channel = check_connection(ctx)
    if not is_connected:
        await ctx.send(messages["not_in_voice_channel"])
    else:
        if vc.is_playing() or vc.is_paused():
            vc.pause()


@bot.command(name="resume")
async def resume(ctx):
    vc, is_connected, is_in_same_channel = check_connection(ctx)
    if not is_connected:
        await ctx.send(messages["not_in_voice_channel"])
    else:
        if vc.is_paused():
            vc.resume()


@bot.event
async def on_ready():
    logger.debug("Bot is ready!")


loop = asyncio.get_event_loop()
loop.create_task(play(q))
loop.run_until_complete(bot.start(TOKEN))
