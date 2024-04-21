# -*- coding: utf-8 -*-
import asyncio

import discord
from discord.ext import commands
from loguru import logger
from settings import AppSettings
from src.utils import add_track_queue, check_connection, play, skip_queue


settings = AppSettings()

TOKEN = settings.TOKEN  # bot's token
download_path = settings.download_path
max_queue_size = settings.max_queue_size  # max number of tracks in queue
command_prefix = settings.command_prefix
messages = settings.get_messages()

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
