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
            # print(member, str(member.id))
            query = """ INSERT INTO users (discord_id, exp, gold, level, stage)
                    VALUES (""" + str(member.id) + """, 1, 1, 1, 1)
                    ON CONFLICT DO NOTHING
                    """
            cur.execute(query)
            conn.commit()

# Displays leaderboad of exp for the server command was called in
@bot.command(name='allexp', help='Shows server members\' exp')
async def all_exp(ctx):
    # ctx.message.content = ctx.message.content.replace(" ", "")
    # ctx.mesage.guild does not contain members, but it does contain the context's guild ID
    # print(ctx.message.guild.id)
    author_id = ctx.author.id

    current_guild = next((g for g in bot.guilds if g.id == ctx.guild.id), None)

    members_map = {}
    for member in current_guild.members:
        members_map[member.id] = member.name

    query = """
        SELECT level, exp FROM users
        WHERE discord_id = %s
        """

    cur.execute(query, (author_id,))
    conn.commit()
    result = cur.fetchall()

    level = result[0][0]
    curr_exp = result[0][1]
    target_exp = pow(2, level)

    # uncommenting this will make it so when someone does !allexp, something like [1/1]
    # or [2/2] doesn't happen. but there has to be a better way. also EXP has the same problem
    # level_up(author_id, curr_exp, target_exp)

    query = "SELECT discord_id, exp, level FROM users WHERE "

    # bad lazy coding
    first_time = True
    for member in current_guild.members:
        if first_time:
            first_time = False
        else:
            query += ' OR '
        query += 'discord_id = ' + str(member.id)
    query += "ORDER BY level DESC, exp DESC"

    cur.execute(query)
    rows = cur.fetchall()

    result = "Rank\n"
    rank = 0
    for row in rows:
        user = str(members_map[row[0]])
        level = row[2]
        exp = str(row[1])
        target_exp = pow(2, level)
        rank += 1

        result += str(rank) + ": [" + user + "] is level [" + str(level) + "] and has [" + exp + "/" + str(target_exp) + "] exp!\n"

    await ctx.send(f"```ini\n{result}\n```")

# Inside jokes
@bot.command(name='joke', help='inside inside jokes')
async def joke(ctx):
    someShit = [
            'HEE HAW',
            'HuDANG',
            'brown bastard',
            'stuipd',
            'speaking!',
            'good noe',
            'Illegal',
            'two deaths tonight',
            'here it comes',
            'oh no',
            'how dare u imply i relieve myself to ink and paper',
            'THEN A PIANO FELL ON MY HEAD',
            'then i got sucked into a wurm hole',
            'hwat.',
            'yinkies',
            'Hugh, Mungus',
            'CLEARLY OF THE WEAKEST'
    ]

    response = random.choice(someShit)
    await ctx.send(response)

# Responds with random answers
@bot.command(name='magicblueball', help='Feeling Lucky?')
async def magicblueball(ctx):
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

# yes
@bot.command(name='yes', help='yes')
async def yes(ctx):
    await ctx.send('Yes')

# Rolls dice, user can input an amount of dice to roll and how many sides all will have.
@bot.command(name='roll', help='Try !roll 2 6 (rolls 2 dice, both with 6 sides')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

# flips a coin
@bot.command(name='coinflip', help='Flips a coin')
async def coinflip(ctx):
    sides = [
        '**HEADS**',
        '**TAILS**'
    ]
    await ctx.send(random.choice(sides))


# holy grail magnum opus
@bot.command(name='stats', help='Displays your stats')
async def stats(ctx):
    member = ctx.author.name
    member_id = ctx.author.id

    query = """
        SELECT level, exp, gold FROM users
        WHERE discord_id = %s
    """

    cur.execute(query, (member_id,))
    result = cur.fetchall()

    # The base to determine exp needed for leveling up
    base = 2

    level = result[0][0]
    curr_exp = result[0][1]
    gold = result[0][2]
    target_exp = pow(base, level)

    level_up(member_id, curr_exp, target_exp)

    total_exp = pow(base, level) + curr_exp - base

    await ctx.send(f"""
            > ***__{member}'s stats__***
            > Level: {level}
            > Total Exp: {total_exp}
            > Current Exp: {curr_exp}/{target_exp}
            > Gold: {gold}
            """)

# Displays user's exp
@bot.command(name='exp', help='Displays your exp')
async def exp(ctx):
        author_id = ctx.author.id

        query = """
            SELECT level, exp FROM users
            WHERE discord_id = %s
        """
        cur.execute(query, (ctx.author.id,))
        conn.commit()

        result = cur.fetchall()
        level = result[0][0]
        curr_exp = result[0][1]
        target_exp = pow(2, level)

        level_up(author_id, curr_exp, target_exp)

        await ctx.send(f"```ini\n[{ctx.author.name}] is level [{level}] and has [{curr_exp}/{target_exp}] exp!\n```")

# idk supposed to make errors pop up? huh?
@bot.event
async def on_error(ctx, *args, **kwargs):
    print(f'{args}')
    raise

# Default response for no command... need to find if discord has built in option
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("No such command")
        raise error

@bot.command(name='travel', help='Your journey begins...')
async def travel(ctx):
    print("travel")
    await ctx.send("hello")
    await ctx.send("Your journey begins, {member}")

@bot.command(name='fetchMessages', help='writes all messages from channel to a txt file')
async def fetch_Messages(ctx):
    channel = ctx.channel
    with open('%s_messages.log' % channel, 'w') as f:
        async for message in ctx.channel.history(oldest_first=True, limit=1000000):
            f.write(f'{message.author}: {message.content}\n')
    await ctx.send("Messages saved to %s_messages.log" % channel)

# Writes to message.log, gives exp to author, and checks if they can level_up
@bot.event
async def on_message(ctx):
    author = ctx.author
    author_id = ctx.author.id
    content = ctx.content

    with open('message.log', 'a') as f:
        f.write(f'{author}: {content}\n')
    print(f'{author}: {content}')


    query = """
        SELECT level, exp FROM users
        WHERE discord_id = %s
        """

    cur.execute(query, (author_id,))
    conn.commit()
    result = cur.fetchall()

    level = result[0][0]
    curr_exp = result[0][1]
    target_exp = pow(2, level)

    exp_up(author_id)
    level_up(author_id, curr_exp, target_exp)

    if (ctx.content.lower() == "!travel"):
        beginStory(author)

    await bot.process_commands(ctx)


def beginStory(author):
    print(f"{author} has began a story!")

# If exp >= 2 ^ level (which is target level) level++
def level_up(author_id, curr_exp, target_exp):

    query = """
        UPDATE users
        SET level = level + 1,
            exp = 0
        WHERE
            discord_id = %s
    """

    if (curr_exp >= target_exp):
        cur.execute(query, (author_id,))
        conn.commit()

# Gain exp on message
def exp_up(author_id):
    query = """
        UPDATE users
        SET exp = exp + 1
        WHERE discord_id = %s
    """
    cur.execute(query, (author_id,))
    conn.commit()

bot.run(TOKEN)

