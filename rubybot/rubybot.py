from discord.ext import commands
from utils import utilities
import logging

debug = False
information = "Welcome to Ruby Bot 2.0! Now rewritten to (hopefully) crash less and require less restarts."
initial_extensions = ['cogs.filterer', 'cogs.twitter', 'cogs.admin']
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename='data/output.log')

if debug:
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


