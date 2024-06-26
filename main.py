# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path

import discord
from discord.ext import commands
from loguru import logger
from settings import AppSettings
from src.utils import (
    add_track_queue,
    check_connection,
    is_user_in_voice_channel,
    play,
    skip_queue,
)


settings = AppSettings()


TOKEN = settings.TOKEN  # bot's token
download_path = settings.download_path
max_queue_size = settings.max_queue_size  # max number of tracks in queue
command_prefix = settings.command_prefix
message_history_length = settings.message_history_length

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
message_history = []


Path(download_path).mkdir(parents=True, exist_ok=True)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        if len(message_history) >= message_history_length:
            bot_msg = message_history.pop(0)
            await bot_msg.delete()
        message_history.append(message)

    await bot.process_commands(message)


@bot.command(name="play")
async def add_track(ctx, *, user_input: str):
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
    await add_track_queue(ctx, user_input, download_path, q, messages)


@bot.command(name="skip-play")
async def skip_add_track(ctx, *, user_input: str):
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
    await skip_queue(ctx, messages)
    await add_track_queue(ctx, user_input, download_path, q, messages)


@bot.command(name="skip")
async def skip(ctx):
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
    await skip_queue(ctx, messages)


@bot.command(name="skip-all")
async def skip_all(ctx):
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
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
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
    vc, is_connected, is_in_same_channel = check_connection(ctx)
    if not is_connected:
        await ctx.send(messages["not_in_voice_channel"])
    else:
        if vc.is_playing() or vc.is_paused():
            vc.pause()


@bot.command(name="resume")
async def resume(ctx):
    if len(message_history) >= message_history_length:
        msg = message_history.pop(0)
        await msg.delete()
    message_history.append(ctx.message)

    if not is_user_in_voice_channel(ctx):
        await ctx.send(messages["user_not_in_voice_channel"])
        return
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
