# -*- coding: utf-8 -*-
import asyncio
import subprocess
from os import listdir
from os.path import isfile, join
from urllib.parse import urlparse

import discord
from loguru import logger


def is_supported(url):
    try:
        if urlparse(url).netloc:
            return True
        return False
    except:
        return False


def check_connection(ctx):
    author_voice_channel_id = ctx.author.voice.channel.id
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client:
        return (
            voice_client,
            voice_client.is_connected(),
            voice_client.channel.id == author_voice_channel_id,
        )
    return None, False, False


def is_user_in_voice_channel(ctx):
    try:
        ctx.author.voice.channel.id
        return True
    except:
        return False


async def download(link, download_path):

    # TODO download queue
    result = subprocess.run(
        [
            "yt-dlp",
            "--no-warnings",
            "-O",
            "fulltitle",
            "-O",
            "id",
            "-O",
            "filename",
            "--no-simulate",
            "-o",
            "%(id)s.%(ext)s",
            "-f ba/b",
            link,
            "-P",
            download_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    result.stdout.rstrip().splitlines()


async def skip_queue(ctx, messages):
    print("eeeeeeeeeeeeeeeeeeeeeeeeee")
    vc, is_connected, is_in_same_channel = check_connection(ctx)
    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    if not is_connected:
        print("ppppppppppppppppppppppppppppppppp")
        await ctx.send(messages["not_in_voice_channel"])
    else:
        print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
        if vc.is_playing() or vc.is_paused():
            vc.stop()


async def add_track_queue(ctx, user_input, download_path, q, messages):
    if ctx.author.voice.channel is None:
        logger.debug(
            f"{ctx.author.global_name} is not in a voice channel and tried to play {user_input}"
        )
        await ctx.send(messages["user_not_in_voice_channel"])
        return

    if not is_supported(user_input):
        logger.debug(
            f"{ctx.author.global_name} tried to play unsupported url: {user_input}"
        )
        await ctx.send(messages["unsupported_url"])
        return
    link = user_input

    if q.full():
        logger.debug(
            f"{ctx.author.global_name} tried to play {user_input} but queue is full"
        )
        await ctx.send(messages["queue_full"])
        return

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-warnings",
                "-O",
                "fulltitle",
                "-O",
                "id",
                "-O",
                "filename",
                "-o",
                "%(id)s.%(ext)s",
                "-f ba/b",
                link,
                "-P",
                download_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        fulltitle, video_id, filename = result.stdout.rstrip().splitlines()

    except Exception as e:
        logger.error("Failed do download link: " + link)
        return

    logger.debug(f"{ctx.author.global_name} plays '{fulltitle}', id: {video_id}")

    if filename in [
        join(download_path, f)
        for f in listdir(download_path)
        if isfile(join(download_path, f))
    ]:
        logger.debug(f"File for '{fulltitle}' already exists, skipping download")

    else:
        logger.debug(f"Started downloading: '{fulltitle}'")

        await download(link, download_path)

        logger.debug(f"Finished downloading: '{fulltitle}'")

    q.put_nowait((filename, fulltitle, ctx, messages))

    logger.debug(f"Added to queue: '{fulltitle}' in {ctx.author.voice.channel.id}")


async def play(q):
    while True:
        filename, fulltitle, ctx, messages = await q.get()
        global_name = ctx.author.global_name

        vc, is_connected, is_in_same_channel = check_connection(ctx)
        voice_channel = ctx.author.voice.channel
        if not is_connected:
            vc = await voice_channel.connect()
            logger.debug(
                f"Connected to vc: {voice_channel.name} id: {voice_channel.id}"
            )
        elif not is_in_same_channel:
            await vc.disconnect()
            vc = await voice_channel.connect()
            logger.debug(
                f"Connected to vc: {voice_channel.name} id: {voice_channel.id}, {discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)}"
            )
        base_message = messages["start_playing"].format(*[global_name, fulltitle])
        if is_connected and not is_in_same_channel:
            await ctx.send(
                base_message
                + messages["move_to_another_channel"].format(*[voice_channel.name])
            )
        else:
            await ctx.send(base_message)

        vc.play(discord.FFmpegPCMAudio(source=filename))
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)
        if q.empty():
            await vc.disconnect()
