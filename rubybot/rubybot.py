from discord.ext import commands
from cogs.utils import utilities

import re

debug = False
information = "Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)\nCreated with 100% stolen code from Chezz and link2110.\nThank you for using Ruby Bot!"
initial_extensions = ['cogs.administrative', 'cogs.music', 'cogs.info', 'cogs.memes', 'cogs.streams']
if debug:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('+'), description=information)
else:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('~'), description=information)


@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))


@bot.event
async def on_error(event, *args, **kwargs):
    print(event)
    print(str(args))
    print(str(kwargs))


@bot.event
async def on_message(message):
    ch = message.channel
    msg = message.content.lower()
    # If the string contains "aquors" and is NOT preceded by a letter and is NOT followed by a letter
    # (i.e. is not hidden inside a word), then we correct the person. The letter "s" is optional.
    if re.search(r"(?<![a-zA-Z])aquor(s?)(?![a-zA-Z])", msg) is not None:
        await bot.send_message(ch, "***AQOURS***")

    await bot.process_commands(message)



if __name__ == "__main__":

    for extension in initial_extensions:
        bot.load_extension(extension)

    credentials = utilities.load_credentials()
    bot_token = credentials['token']

    bot.run(bot_token)


