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
    print("huh:", e)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    test = 1

    for guild in bot.guilds:
        for member in guild.members:
            print(member, str(member.id))
            cur.execute("""
                    INSERT INTO users (discord_id, exp, gold)
                    VALUES
                    (""" + str(member.id) + """, 0, 0)
                    ON CONFLICT DO NOTHING
            """)
            conn.commit()

@bot.command(name='yes', help='yes')
async def yes(ctx):
    someShit = [
            'Yes',
    ]

    response = random.choice(someShit)
    await ctx.send(response)
    print(f'Someone used the !yes command')

@bot.command(name='roll', help='Try !roll 2 6')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='coinflip', help='The name is obvious hahahaha')
async def coinflip(ctx):
    sides = [
        '**HEADS**',
        '**TAILS**'
    ]
    await ctx.send(random.choice(sides))


@bot.event
async def on_error(event, *args, **kwargs):
    #print(f'{args[0]}')
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_message(message):
    with open('message.log', 'a') as f:
        f.write(f'{message.author}: {message.content}\n')
    #THIS IS WHAT I WANT
    #1. who sent message use discord id
    #2. add 1 to exp
    print(f'{message.author.id}: {message.content}\n')
    cur.execute("""
        UPDATE users
        SET exp = exp + 1
        WHERE discord_id = %s
        RETURNING exp
    """, (message.author.id,))
    print(message.author.id)
    conn.commit()
    hello = cur.fetchone()
    print(hello)
    await bot.process_commands(message)

bot.run(TOKEN)

