# bot.py
import os
import psycopg2
import random
from dotenv import load_dotenv

from discord.ext import commands


try:
    conn = psycopg2.connect(
            user = "wang",
            password = "password",
            host = "127.0.0.1",
            port = "5432",
            database = "botdb")

    cur = conn.cursor()
except Exception as e:
    print("gay:", e)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#    for guild in bot.guilds:
#        print(guild.members)



@bot.command(name='yes', help='yes')
async def yes(ctx):
    someShit = [
            'Yes',
    ]

    response = random.choice(someShit)
    await ctx.send(response)
    print(f'Someone used !yes command')

@bot.command(name='roll', help='Try !roll 2 6')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='coinflip')
async def coinflip(ctx):
    sides = [
        '**HEADS**',
        '**TAILS**'
    ]
    await ctx.send(random.choice(sides))

@bot.event
async def on_error(event, *args, **kwargs):
    print(f'{args[0]}')
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_message(message):
    with open('message.log', 'a') as f:
        f.write(f'{message.author}\n{message.content}\n')
    print(f'{message.author}\n{message.content}\n')
    await bot.process_commands(message)

bot.run(TOKEN)

