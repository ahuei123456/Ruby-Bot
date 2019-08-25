from discord.ext import commands
from utils import utilities
import logging
import re

debug = False
information = "Welcome to Ruby Bot 2.0! Now rewritten to (hopefully) crash less and require less restarts."
initial_extensions = ['cogs.twitter']
logger = logging.getLogger(__name__)

if debug:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('+'), description=information)
else:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('~'), description=information)


@bot.event
async def on_ready():
    logger.info(f'Logged in as:\n{bot.user} (ID: {bot.user.id})')


@bot.event
async def on_message(message):
    msg = message.content.lower()
    # If the string contains "aquors" and is NOT preceded by a letter and is NOT followed by a letter
    # (i.e. is not hidden inside a word), then we correct the person. The letter "s" is optional.
    if re.search(r"(?<![a-zA-Z])aquor(s?)(?![a-zA-Z])", msg) is not None:
        ctx = await bot.get_context(message)
        await ctx.send("***AQOURS***")

    await bot.process_commands(message)


if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)

    credentials = utilities.load_credentials()
    bot_token = credentials['discord']['token']

    bot.run(bot_token)


