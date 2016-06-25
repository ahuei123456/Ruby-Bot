from discord.ext import commands
from cogs.utils import utilities
from cogs.utils import checks
from cogs import streams
import re

information = "Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)\nCreated with 100% stolen code from Chezz and link2110.\nThank you for using Ruby Bot!"
bot = commands.Bot(command_prefix=commands.when_mentioned_or('~'), description=information)

initial_extensions = ['cogs.administrative', 'cogs.music', 'cogs.info', 'cogs.memes']
#osts = streams.Streams(bot)


@bot.event
async def on_ready():
    global posts
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
    await posts.stream()
    try:
        bot.add_cog(posts)
    except Exception:
        print('couldnt add stream????')


@bot.event
async def on_error(event, *args, **kwargs):
    print(event)
    print(str(args))
    print(str(kwargs))


@bot.event
async def on_resumed():
    print('Resumed')
    await posts.reboot_stream()


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
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
            print('failed to load extension {}'.format(extension))

    credentials = utilities.load_credentials()
    bot_token = credentials['token']
    while True:
        try:
            bot.run(bot_token)
        except Exception:
            pass
    print('How da fuck did this get here')


