import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pytimeparse import parse
import datetime
import asyncio
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = '''Im a garbage collector, i clean up old messages. \n type: -gc commands to see a list of commands.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='-gc ', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await startup()


async def collect(channelId, time_delta : datetime.timedelta):
    channel = bot.get_channel(channelId)
    try:
        if not isinstance(channel, discord.TextChannel):
            return
        utc = datetime.datetime.now()-time_delta
        msg_list = await channel.purge(limit=100, before=utc)
        if len(msg_list) > 0:
            print(f'purged {len(msg_list)} from {channelId}')

    except discord.errors.Forbidden:
        print('error')
        pass

def get_delta(time, time_format):
    time_formats = {
        "s": datetime.timedelta(seconds=float(time)),
        "m": datetime.timedelta(minutes=float(time)),
        "h": datetime.timedelta(hours=float(time)),
        "d": datetime.timedelta(days=float(time))
    }
    return time_formats[time_format]


async def timeout(channelId, time_delta : datetime.timedelta):

    print(f'timeout set for channel [{channelId}], removing messages older than {time_delta}')
    while True:
        await collect(channelId, time_delta)
        await asyncio.sleep(1)


async def write_json(channelId, delta):
    obj = {
        "channel":channelId,
        "time_delta": str(delta)
    }
    id_occurs = False
    with open('timers.json', 'r+') as f:
        file_data = json.load(f)
        for e in file_data:
             if channelId == e['channel']:
                e['time_delta'] = str(delta)
                id_occurs = True
        if not id_occurs: file_data.append(obj)

        f.seek(0)
        json.dump(file_data, f, indent = 4)
        f.close()


@bot.command()
async def timer(ctx, timer:str):
    if not ctx.message.author.guild_permissions.administrator:  
        print(f'unauthorized request on command "timer" from {ctx.message.author}')
        return
    await ctx.message.delete()
    time_format = ''.join([i for i in timer if not i.isdigit()])
    if not time_format:
        await ctx.send('invalid time format')
        return
    num = ''.join([i for i in timer if i.isdigit()])
    delta = get_delta(num, time_format)
    await write_json(ctx.channel.id, delta)
    try:
        task, = [task for task in asyncio.all_tasks() if task.get_name() == str(ctx.channel.id)]
        task.cancel()
    except:
        print('current channel has no timeout running')

    asyncio.create_task(timeout(ctx.channel.id, delta), name=str(ctx.channel.id))

    
    
@bot.command()
async def commands(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        print(f'unauthorized request on command "commands" from {ctx.message.author}')
        return
    await ctx.message.delete()
    embed = discord.Embed(
        title='Garbage Collector Commands',
        color=discord.Color.blurple())
    embed.add_field(name='Set Timeout | "-gc timer <amount<format>>"', value=' e.g. "-gc timer 10d" removes messages older than 10days', inline=False)
    embed.add_field(name='Disable Timeout | "-gc disable"', value='Remove the current timeout in the channel', inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def disable(ctx):
    if not ctx.message.author.guild_permissions.administrator:   
        print(f'unauthorized request on command "disable" from {ctx.message.author}')
        return
    await ctx.message.delete()
    try:
        task, = [task for task in asyncio.all_tasks() if task.get_name() == str(ctx.channel.id)]
        task.cancel()
    except:
        print('current channel has no timeout running')
    with open('timers.json', 'r+') as f:
        file_data = json.load(f)
        for i in range (len(file_data)):
             if ctx.channel.id == file_data[i]['channel']:
                del file_data[i]
                break
    f = open('timers.json', 'w')
    f.write(json.dumps(file_data, indent = 4))
    f.close()
    print(f'disabled timeout in channel {ctx.channel.id}')


@bot.command()
async def info(ctx):
    if not ctx.message.author.guild_permissions.administrator:  
        print(f'unauthorized request on command "info" from {ctx.message.author}')
        return
    threads = asyncio.all_tasks()
    for t in threads: print(t)
    print(len(asyncio.all_tasks()))
    await ctx.message.delete()
    await ctx.send(f'Current registered tasks: {len(asyncio.all_tasks())}')


async def startup():
    print('resuming saved timers')
    f = open('timers.json', 'r')
    timers = json.loads(f.read())
    f.close()
    for e in timers:
        t = parse(e['time_delta'])
        asyncio.create_task(timeout(int(e['channel']), datetime.timedelta(seconds=t)), name=e['channel'])
        print('created task')

bot.run(TOKEN)