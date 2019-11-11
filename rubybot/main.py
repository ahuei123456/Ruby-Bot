from discord.ext import commands
import json
import logging
import os
import sys

sys.path.insert(0, os.getcwd())

from rubybot.utils import utilities

with open(os.path.join(os.getcwd(), 'rubybot', 'conf', 'test.json')) as f:
    data = json.load(f)

os.environ['TEST'] = data['test']

information = "Welcome to Ruby Bot 2.0! Now rewritten to (hopefully) crash less and require less restarts."
initial_extensions = ['rubybot.cogs.filterer', 'rubybot.cogs.twitter', 'rubybot.cogs.admin']
logging.basicConfig(level=logging.INFO, filename=os.path.join(os.getcwd(), 'rubybot', 'data', 'output.log'))
logger = logging.getLogger(__name__)

if int(os.environ['TEST']) == 1:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('+'), description=information)
else:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('~'), description=information)


@bot.event
async def on_ready():
    logger.info(f'Logged in as:\n{bot.user} (ID: {bot.user.id})')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


if __name__ == "__main__":

    for extension in initial_extensions:
        bot.load_extension(extension)

    credentials = utilities.load_credentials()
    bot_token = credentials['discord']['token']

    bot.run(bot_token)


