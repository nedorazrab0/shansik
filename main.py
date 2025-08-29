#!/usr/bin/env python3
#
# shansik bot

from string import ascii_letters, digits, punctuation
from urllib.parse import quote_plus
from subprocess import check_output
from random import randint, choice
from zoneinfo import ZoneInfo
from datetime import datetime
from os import environ
from re import match
from gpytranslate import Translator
from nextcord.ext import commands
from nextcord import Intents
from aiohttp import ClientSession
from orjson import loads

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

@bot.command(help="flip a coin")
async def coin(ctx):
    rand = randint(0, 1)
    if rand == 1:
        result = "i cant stop winning"
    else:
        result = "oh dang it"
    await reply(ctx, result)

@bot.command(help="russian roulette roll")
async def rule(ctx):
    rand = randint(0, 5)
    if rand == 5:
        result = "ALAH BABAH"
    else:
        result = "you are lucky"
    await reply(ctx, result)

@bot.command(help="get shows order for target points, 4* 0MR"
                  + " (50% EB) and 1* 5MR (2% EB)")
async def pk(ctx, target_points):
    order = check_output(["/usr/bin/python3", "./spc", "-p", target_points])
    result = str(order, "utf-8")
    await reply(ctx, result)

@bot.command(help="get leaderboard, 1 page = 50 tiers  (e.g. 2 nowl kr)")
async def lb(ctx, page, wl="nowl", reg="en"):
    if wl == "wl":
        url = "https://api.sekai.best/event/live_latest_chapter?region=" + reg
    elif wl == "nowl":
        url = "https://api.sekai.best/event/live?region=" + reg

    if int(page) == 1:
        tops = range(0, 51)
    else:
        tops = range(50, 103)

    raw = await sget(url)
    json = loads(raw)
    ranks = json["data"]["eventRankings"]

    leaderboard = ""
    for top in tops:
        user = ranks[top]
        rank = user["rank"]
        name = user["userName"]
        score = user["score"]
        leaderboard += str(rank) + '  "' + name[:20] + '"  ' + str(score) + "\n"
    result = "```\n" + leaderboard + "```"
    await reply(ctx, result)

@bot.command(help="send random line of anti anti you")
async def au(ctx):
    line = check_output(["/usr/bin/python3", "./randomantiyou"])
    result = str(line, "utf-8")
    await reply(ctx, result)

@bot.command(help="convert r g b to hex")
async def hex(ctx, r, g, b):
    result = "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
    await reply(ctx, result)

@bot.command(help="get a value for compare isvs")
async def isv(ctx, leader_skill, team_skill):
    result = int(leader_skill)*4 + int(team_skill) - 90
    await reply(ctx, result)

@bot.command(help="convert hex to r g b")
async def rgb(ctx, rawhex):
    hex = rawhex.lstrip("#")
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)

    result = str(r) + " " + str(g) + " " + str(b)
    await reply(ctx, result)

@bot.command(help="change room code")
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
            result = "invalid room code"
    else:
        result = "the channel name must be like this luka22-12345"
    await reply(ctx, result)

@bot.command(help="convert type year month day h m to timestamp (types t,R,F)")
async def ts(ctx, type, year, month, day, h, m):
    if match("t|T|d|D|f|F|R", type):
        date = datetime(int(year), int(month), int(day), int(h), int(m), 0)
        timestamp = str(int(date.timestamp()))
        result = "<t:" + timestamp + ":" + type + ">"
    else:
        result = "invalid type"
    await reply(ctx, result)

@bot.command(help="convert timezone (e.g. Europe/Moscow UTC 2022 12 31 23)")
async def tz(ctx, source_zone, target_zone, year, month, day, h):
    date = datetime(int(year), int(month), int(day), int(h),
                    tzinfo=ZoneInfo(source_zone))
    d = date.astimezone(ZoneInfo(target_zone))
    result = (str(d.year) + " " + str(d.month) + " " + str(d.day) + " "
              + str(d.hour))
    await reply(ctx, result)

@bot.command(help="convert sizeunits (e.g. 10 gb mb)")
async def sz(ctx, num, sizeunit1, sizeunit2):
    sizeunits = {"b": 8, "kb": 10**3, "mb": 10**6, "gb": 10**9, "tb": 10**12, 
                 "kib": 2**10, "mib": 2**20, "gib": 2**30, "tib": 2**40}
    converted = (int(num)*sizeunits[sizeunit1])/sizeunits[sizeunit2]
    result = round(converted, 1)
    await reply(ctx, result)

@bot.command(help="pick a random item of specified ones")
async def pick(ctx, *items):
    result = choice(items)
    await reply(ctx, result)

@bot.command(help="get the lenght of text, do not forget about quotes")
async def ln(ctx, text):
    result = len(text)
    await reply(ctx, result)

@bot.command(help="translate the text ('my text', lang)")
async def tr(ctx, text, tolang="en"):
    result = await translate(text, tolang)
    await reply(ctx, result)

@bot.command(help="send an extract of random wiki page")
async def wk(ctx):
    lang = "ru"
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

    result = await translate(text, lang)
    await reply(ctx, result)

@bot.command(help="calculator")
async def c(ctx, mathstr):
    if match('[a-zA-Z]', mathstr):
        result = "do not use any letters"
    else:
        result = eval(mathstr.upper())
    await reply(ctx, result)

@bot.command(help="get the weather in specified location")
async def wt(ctx, loc, lang="ru"):
    url = "https://wttr.in/" + loc + "?format=%t+%C+%uuw+%T&m&lang=" + lang
    result = await sget(url)
    await reply(ctx, result)

@bot.command(help="repeat the text n times (repeats, 'text')")
async def rp(ctx, repeats=79, text="z"):
    if repeats > 2000:
        result = "too many repeats"
    else:
        result = "".join(text for i in range(int(repeats)))
    await reply(ctx, result)

@bot.command(help="send a random string")
async def rns(ctx):
    rand = "".join(choice(ascii_letters + digits + punctuation)
                   for i in range(20))
    result = "```\n" + rand + "\n```"
    await reply(ctx, result)

@bot.command(help="send a random num, start stop")
async def rn(ctx, start=1, stop=100):
    result = randint(int(start), int(stop))
    await reply(ctx, result)

@bot.command(help="jason pic")
async def jason(ctx):
    result = "<:jason:1410289021263020144>"
    await reply(ctx, result)

@bot.command(help="taph pic")
async def taph(ctx):
    result = "<:taph:1410288947619303484>"
    await reply(ctx, result)

@bot.command(help="saki pic")
async def saki(ctx):
    result = "<:saki:1410288878828388412>"
    await reply(ctx, result)

@bot.command(help="teehee pic")
async def teehee(ctx):
    result = "<:teehee:1410288750742995078>"
    await reply(ctx, result)

@bot.command(help="patpat pic")
async def patpat(ctx):
    result = "<a:patpat:1410053978921762867>"
    await reply(ctx, result)

@bot.command(help="kanade pic")
async def kana(ctx):
    result = "<a:kanade:1410053899859267645>"
    await reply(ctx, result)

@bot.command(help="an pic")
async def an(ctx):
    result = "<a:an:1410053927759646810>"
    await reply(ctx, result)

@bot.command(help="white pic")
async def white(ctx):
    result = "<a:white:1410053954494267485>"
    await reply(ctx, result)

@bot.command(help="generate a qr code from text")
async def qr(ctx, text):
    url = ("https://api.qrserver.com/v1/create-qr-code/?size=1000x1000"
           + "&format=png&data=" + quote_plus(text, safe=""))
    result = url
    await reply(ctx, result)

@bot.command(help="send a random safebooru img")
async def img(ctx):
    url = ("https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1"
           + "&limit=1&random=true")
    raw = await sget(url)
    json = loads(raw)
    file_url = json[0]["file_url"]
    result = file_url.lstrip("\\")
    await reply(ctx, result)

@bot.command(help="check is bot alive")
async def w(ctx):
    result = "goddamn whatsup"
    await reply(ctx, result)

async def reply(ctx, result):
    await ctx.reply(result, mention_author=False)

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
