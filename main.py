#!/usr/bin/env python3
#
# shansik bot

from string import ascii_letters, digits, punctuation
from urllib.parse import quote_plus
from subprocess import check_output
from random import randint, choice
from datetime import datetime
from os import environ
from re import match
from nextcord import Intents, Client, Game, Interaction, SlashOption, Member
from nextcord.ext import commands
from gpytranslate import Translator
from aiohttp import ClientSession
from orjson import loads

activity = Game(name="pisun")
intents = Intents.default()
bot = commands.Bot(intents=intents, activity=activity)

@bot.slash_command(description="flip a coin")
async def coin(ctx):
    result = choice(["i cant stop winning", "oh dang it"])
    await reply(ctx, result)

@bot.slash_command(description="russian roulette roll")
async def rule(ctx):
    rand = randint(0, 5)
    if rand == 5:
        result = "ALAH BABAH"
    else:
        result = "you are lucky"
    await reply(ctx, result)

@bot.slash_command(description="pick a random item of specified ones")
async def pick(ctx, items: str):
    result = choice(items.split())
    await reply(ctx, result)

@bot.slash_command(description="shows order, 4* 0MR (50% EB) and 1* 5MR (2% EB)")
async def park(ctx, target_points):
    order = check_output(["/usr/bin/python3", "./spc", "-p", target_points])
    result = str(order, "utf-8")
    await reply(ctx, result)

@bot.slash_command(description="get sekai leaderboard")
async def leaderboard(
    ctx: Interaction,
    page: int = SlashOption(choices=[1, 2]),
    region: str = SlashOption(choices=["en", "kr", "jp", "tw", "cn"]),
    wl: bool = SlashOption(choices=[True, False]),
):
    if wl:
        type = "live_latest_chapter"
    else:
        type = "live"
    url = f"https://api.sekai.best/event/{type}?region={region}"
    if page == 1:
        tops = range(0, 51)
    elif page == 2:
        tops = range(50, 103)
    raw = await sget(url)
    json = loads(raw)
    data = json["data"]["eventRankings"]
    leaderboard = "".join(f"{data[top]['rank']}  {data[top]['userName'][:20]}"
                          + f"  {data[top]['score']}\n" for top in tops)
    result = "```\n" + leaderboard + "```"
    await reply(ctx, result)

@bot.slash_command(description="check is api.sekai.best alive")
async def api_check(ctx):
    url = "https://api.sekai.best/status"
    statusurl = "https://status.sekai.best/history/api"
    raw = sget(url)
    if raw is None:
        result = f"[api.sekai.best]({statusurl}) umer"
    else:
        result = f"[api.sekai.best]({statusurl}) is alive"
    await reply(ctx, result)

@bot.slash_command(description="send random line of anti anti you")
async def antiyou(ctx):
    line = check_output(["/usr/bin/python3", "./randomantiyou"])
    result = str(line, "utf-8")
    await reply(ctx, result)

@bot.slash_command(description="convert rgb to hex")
async def hex(ctx, red: int, green: int, blue: int):
    result = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    await reply(ctx, result)

@bot.slash_command(description="get a value for compare isvs")
async def isv(ctx, leader_skill: int, team_skill: int):
    result = leader_skill*4 + team_skill - 90
    await reply(ctx, result)

@bot.slash_command(description="convert hex to r g b")
async def rgb(ctx, hex: str):
    hex = hex.lstrip("#")
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)

    result = f"{r} {g} {b}"
    await reply(ctx, result)

@bot.slash_command(description="change room code")
async def rm(ctx, code):
    ch = ctx.channel
    regex = ".[0-9].*-[0-9|x][0-9|x][0-9|x][0-9|x][0-9|x]"
    if match(regex, ch.name):
        matchname = match(".[0-9]-", ch.name)
        rmname = matchname[0]
        new_name = rmname + code
        if match(regex, new_name):
            await ch.edit(name=new_name)
            result = "room code changed"
        else:
            new_name = rmname + "xxxxx"
            await ch.edit(name=new_name)
            result = "room closed, lets go gambling"
    else:
        result = "the channel name must be like this luka22-12345"
    await reply(ctx, result)

@bot.slash_command(description="convert UTC to timestamp")
async def timestamp(
    ctx: Interaction,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    type: str = SlashOption(choices={"t time short": "t", "T time long": "T",
                                     "d date short": "d", "D date long": "D",
                                     "f D+t": "f", "F very long": "F",
                                     "R timeleft": "R"})
):
    date = datetime(year, month, day, hour, minute, 0)
    timestamp = str(int(date.timestamp()))
    result = "<t:" + timestamp + ":" + type + ">"
    await reply(ctx, result)

@bot.slash_command(description="convert timezone")
async def timezone(
    ctx: Interaction,
    hour: int,
    source_zone: int = SlashOption(choices=[-12, -11, -10, -9, -8, -7, -6, -5,
                                            -4, -3, -2, -1, 0, 1, 2, 3, 4, 5,
                                            6, 7, 8, 9, 10, 11, 12]),
    target_zone: int = SlashOption(choices=[-12, -11, -10, -9, -8, -7, -6, -5,
                                            -4, -3, -2, -1, 0, 1, 2, 3, 4, 5,
                                            6, 7, 8, 9, 10, 11, 12])
):
    converted = hour + source_zone + target_zone
    if converted > 24:
        result = f"{converted - 24} of the next day"
    elif converted < 0:
        result = f"{converted + 24} of the previous day"
    else:
        result = f"{converted} of the same day"
    await reply(ctx, result)

@bot.slash_command(description="convert sizeunits")
async def sizeconvert(ctx, num: int, sizeunit1, sizeunit2):
    sizeunits = {"bit": 1, "b": 8,
                 "kb": 10**3*8, "mb": 10**6*8, "gb": 10**9*8, "tb": 10**12*8,
                 "kibit": 2**10, "mibit": 2**20, "gibit": 2**30, "tibit": 2**40,
                 "kbit": 10**3, "mbit": 10**6, "gbit": 10**9, "tbit": 10**12,
                 "kib": 2**10*8, "mib": 2**20*8, "gib": 2**30*8, "tib": 2**40*8}
    converted = (num*sizeunits[sizeunit1])/sizeunits[sizeunit2]
    result = round(converted, 1)
    await reply(ctx, result)

@bot.slash_command(description="get the lenght of text")
async def ln(ctx, text):
    result = len(text)
    await reply(ctx, result)

@bot.slash_command(description="translate the text")
async def tra(ctx, text: str, lang: str):
    result = await translate(text, lang)
    await reply(ctx, result)

@bot.slash_command(description="send an extract of random wiki page")
async def wiki(ctx):
    wikiurl = "https://en.wikipedia.org/w/"
    sekaipediaurl = "https://www.sekaipedia.org/w/"
    opts = ("api.php?format=json&action=query&explaintext&generator=random"
            + "&grnnamespace=0&prop=extracts&grnlimit=1&exintro&redirects=")
    rand = randint(0, 2)
    if rand == 2:
        url = sekaipediaurl + opts + "/en"
    else:
        url = wikiurl + opts
    page = await sget(url)
    json = loads(page)
    id = str(*json["query"]["pages"])
    text = json["query"]["pages"][id]["extract"]
    result = await translate(text, "ru")
    await reply(ctx, result)

@bot.slash_command(description="calculator")
async def calculate(ctx, expr):
    if match('[a-zA-Z]', expr):
        result = "do not use any letters"
    else:
        result = eval(expr.upper())
    await reply(ctx, result)

@bot.slash_command(description="get the weather in specified location")
async def weather(ctx, location):
    url = f"https://wttr.in/{location}?format=%t+%C+%uuw+%T&m&lang=ru"
    result = await sget(url)
    await reply(ctx, result)

@bot.slash_command(description="repeat the text n times")
async def repeat(ctx, repeats: int, text: str):
    if repeats > 2000:
        result = "too many repeats"
    else:
        text = "".join(text for i in range(int(repeats)))
        result = text[:2000]
    await reply(ctx, result)

@bot.slash_command(description="send a random string")
async def random_str(ctx):
    rand = "".join(choice(ascii_letters + digits + punctuation)
                   for i in range(20))
    result = "```\n" + rand + "\n```"
    await reply(ctx, result)

@bot.slash_command(description="send a random num")
async def random(ctx, start: int, stop: int):
    result = randint(start, stop)
    await reply(ctx, result)

@bot.slash_command(description="jason pic")
async def jason(ctx):
    result = "<:jason:1410289021263020144>"
    await reply(ctx, result)

@bot.slash_command(description="taph pic")
async def taph(ctx):
    result = "<:taph:1410288947619303484>"
    await reply(ctx, result)

@bot.slash_command(description="saki pic")
async def saki(ctx):
    result = "<:saki:1410288878828388412>"
    await reply(ctx, result)

@bot.slash_command(description="teehee pic")
async def teehee(ctx):
    result = "<:teehee:1410288750742995078>"
    await reply(ctx, result)

@bot.slash_command(description="patpat pic")
async def patpat(ctx):
    result = "<a:patpat:1410053978921762867>"
    await reply(ctx, result)

@bot.slash_command(description="kanade pic")
async def kana(ctx):
    result = "<a:kanade:1410053899859267645>"
    await reply(ctx, result)

@bot.slash_command(description="an pic")
async def an(ctx):
    result = "<a:an:1410053927759646810>"
    await reply(ctx, result)

@bot.slash_command(description="white pic")
async def white(ctx):
    result = "<a:white:1410053954494267485>"
    await reply(ctx, result)

@bot.slash_command(description="generate a qr code from text")
async def qr(ctx, text):
    url = ("https://api.qrserver.com/v1/create-qr-code/?size=1000x1000"
           + "&format=png&data=" + quote_plus(text, safe=""))
    result = url
    await reply(ctx, result)

@bot.slash_command(description="hug a user")
async def hug(ctx, user: Member):
    url = "https://nekos.life/api/v2/img/hug"
    raw = await sget(url)
    json = loads(raw)
    result = f"{user.mention}[))))]({json['url']})"
    await reply(ctx, result)

@bot.slash_command(description="send a random safebooru img")
async def img(ctx):
    url = ("https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1"
           + "&limit=1&random=true")
    raw = await sget(url)
    json = loads(raw)
    file_url = json[0]["file_url"]
    result = file_url.lstrip("\\")
    await reply(ctx, result)

@bot.slash_command(description="check is bot alive")
async def bot_check(ctx):
    result = "goddamn whatsup"
    await reply(ctx, result)

async def reply(ctx, result):
    await ctx.response.send_message(result)

async def sget(url):
    headers = ({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                + "AppleWebKit/537.36 (KHTML, like Gecko)"
                + "Chrome/100.0.4896.127 Safari/537.36"})
    async with ClientSession() as s:
        async with s.get(url, headers=headers) as resp:
            return await resp.text()

async def translate(text, lang):
    t = Translator()
    result = await t.translate(text[:690], targetlang=lang)
    return result

token = environ["TOKEN"]
bot.run(token)
