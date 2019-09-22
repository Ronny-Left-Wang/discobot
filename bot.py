# bot.py
import os
import random
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    someShit = [
            'I am bot created by Ronny, Amazing.',
            'Ronny\'s bot I am.',
            'Currently working on bot code.',
            'Yes',
            'Yes',
            'Maybe'
    ]

    if 'xd' in message.content.lower():
        response = random.choice(someShit)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(token)

'''
client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=guild)
    print(
        f'{client.user} has connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

client.run(token)
'''
