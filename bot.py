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
            query = """ INSERT INTO users (discord_id, exp, gold, level)
                    VALUES (""" + str(member.id) + """, 1, 1, 1)
                    ON CONFLICT DO NOTHING
                    """
            cur.execute(query)
            conn.commit()

@bot.command(name='allexp', help='Shows server members\' exp')
async def allExp(ctx):
    # ctx.message.content = ctx.message.content.replace(" ", "")
    # ctx.mesage.guild does not contain members, but it does contain the context's guild ID
    # print(ctx.message.guild.id)

    current_guild = next((g for g in bot.guilds if g.id == ctx.guild.id), None)

    members_map = {}
    for member in current_guild.members:
        members_map[member.id] = member.name

    levelUp()

    query = "SELECT discord_id, exp, level FROM users WHERE "

    # bad lazy coding
    first_time = True;
    for member in current_guild.members:
        if first_time:
            first_time = False
        else:
            query += ' OR ';
        query += 'discord_id = ' + str(member.id)
    query += "ORDER BY level DESC, exp DESC"

    cur.execute(query)
    rows = cur.fetchall()

    levelUp()

    result = "Rank\n"
    rank = 0
    for row in rows:
        user = str(members_map[row[0]])
        level = row[2]
        exp = str(row[1])
        targetExp = pow(2, level)
        rank += 1

        result += str(rank) + ": [" + user + "] is level [" + str(level) + "] and has [" + exp + "/" + str(targetExp) + "] exp!\n"

    await ctx.send(f"```ini\n{result}\n```")

@bot.command(name='joke', help='inside inside jokes')
async def yes(ctx):
    someShit = [
            'HEE HAW',
            'HuDANG',
            'brown bastard',
            'stuipd',
            'bwain ndamg',
            'speaking!',
            'the time has come, and so have I',
            'good!',
            'good noe',
            'Illegal',
            'two deaths tonight',
            'here it comes',
            'oh no',
            'joke on u',
            'how dare u imply i relieve myself to ink and paper',
            'jerkin it',
            'u wanna get outta here?',
            'THEN A PIANO FELL ON MY HEAD',
            'then i got sucked into a wurm hole',
            'hwat.',
            'yinkies',
            'ee-no-mus',
    ]

    response = random.choice(someShit)
    await ctx.send(response)

@bot.command(name='magicblueball', help='Feeling Lucky?')
async def yes(ctx):
    someShit = [
            'Yes',
            'No',
            'Maybe',
            'It is certain',
            'Sorry, try again',
            'Impossible',
            'Probable',
            'Unlikely',
            '*Heads*',
            '*TAILS*',
            'Nah',
            'Yeahhh',
    ]

    response = random.choice(someShit)
    await ctx.send(response)

@bot.command(name='yes', help='yes')
async def yes(ctx):
    await ctx.send('Yes')

@bot.command(name='roll', help='Try !roll 2 6 (rolls 2 dice, both with 6 sides')
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
    # create  stats?
    query = """
        SELECT level, exp FROM users
        WHERE discord_id = %s
    """
    cur.execute(query, (ctx.author.id,))
    conn.commit()

    result = cur.fetchall()
    level = result[0][0]
    exp = result[0][1]

    levelUp()

    targetExp = pow(2, level)
    await ctx.send(f"```ini\n[{ctx.author.name}] is level [{level}] and has [{exp}/{targetExp}] exp!\n```")

@bot.event
async def on_error(ctx, *args, **kwargs):
    print(f'{args[0]}')
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

    expUp(ctx.author.id)
    levelUp()

    await bot.process_commands(ctx)

# If exp >= 2 ^ level (which is target level) level++
def levelUp():
    query = """
        UPDATE users
        SET level = level + 1,
            exp = 0
        WHERE
            exp >= POWER(2, level)
    """
    cur.execute(query)
    conn.commit()

# Gain exp on message
def expUp(author_id):
    query = """
        UPDATE users
        SET exp = exp + 1
        WHERE discord_id = %s
    """
    cur.execute(query, (author_id,))
    conn.commit()

bot.run(TOKEN)

