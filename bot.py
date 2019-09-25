# bot.py
import os
import psycopg2
import random
from dotenv import load_dotenv

from discord.ext import commands
from discord.ext.commands import CommandNotFound

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

    for guild in bot.guilds:
        for member in guild.members:
            #print(member, str(member.id))
            cur.execute("""
                    INSERT INTO users (discord_id, exp, gold, level)
                    VALUES
                    (""" + str(member.id) + """, 0, 0, 0)
                    ON CONFLICT DO NOTHING
            """)
            conn.commit()

@bot.command(name='allExp', help='Shows server members\' exp')
async def allExp(ctx):
    # ctx.mesage.guild does not contain members, but it does contain the context's guild ID
    # print(ctx.message.guild.id)

    current_guild = next((g for g in bot.guilds if g.id == ctx.guild.id), None)

    members_map = {}
    for member in current_guild.members:
        members_map[member.id] = member.name

    #query2 = "UPDATE users SET level = LOG(2, exp)"
    #cur.execute(query2)
    #conn.commit()
    query = "SELECT discord_id, exp, level FROM users WHERE ";

    # bad lazy coding
    first_time = True;
    for member in current_guild.members:
        if first_time:
            first_time = False;
        else:
            query += ' OR ';
        query += 'discord_id = ' + str(member.id)
    query += "ORDER BY exp DESC";

    cur.execute(query)
    rows = cur.fetchall()

    result = ""
    for row in rows:
        result += str(members_map[row[0]]) + " is level " + str(row[2]) + " has [" + str(row[1]) + "] exp!\n"

    await ctx.send(f"```ini\n{result}\n```")

@bot.command(name='jokes', help='inside inside jokes')
async def yes(ctx):
    someShit = [
            'HEE HAW',
            'HuDANG',
            'brown bastard',
            'stuipd',
            'bwain ndamg',
            'speaking!',
            'good!',
            'good noe',
            'Illegal',
            'two deaths tonight',
            'here it comes',
    ]

    response = random.choice(someShit)
    response = '!jokes'
    await ctx.send(response)

@bot.command(name='yes', help='yes')
async def yes(ctx):
    someShit = [
            'Yes',
    ]

    response = random.choice(someShit)
    print(f'{ctx.author.name} used the !yes command')
    await ctx.send(response)

@bot.command(name='roll', help='Try !roll 2 6')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='coinflip', help='Flips a coin')
async def coinflip(ctx):
    sides = [
        '**HEADS**',
        '**TAILS**'
    ]
    await ctx.send(random.choice(sides))

@bot.command(name='exp', help='Returns your exp')
async def exp(ctx):
    cur.execute("""
        SELECT exp FROM users
        WHERE discord_id = %s
    """, (ctx.author.id,))
    conn.commit()
    totalExp = cur.fetchone()[0]
    await ctx.send(f"{ctx.author.name} has {totalExp} exp!")

@bot.event
async def on_error(ctx, *args, **kwargs):
    #print(f'{args[0]}')
    with open('err.log', 'a') as f:
        if ctx == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("No such command")
        # raise error

@bot.event
async def on_message(ctx):
    with open('message.log', 'a') as f:
        f.write(f'{ctx.author}: {ctx.content}\n')
    print(f'{ctx.author}: {ctx.content}')
    cur.execute("""
        UPDATE users
        SET exp = exp + 1
        WHERE discord_id = %s
        RETURNING exp
    """, (ctx.author.id,))
    conn.commit()
    await bot.process_commands(ctx)

bot.run(TOKEN)

