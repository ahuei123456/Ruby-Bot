from discord.ext import commands
from cogs.utils import utilities

information = "Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)\nLyrical display updated! Use lyrics <title> to display the lyrics of any LL song!.\nThank you for using Ruby Bot!"
bot = commands.Bot(command_prefix=commands.when_mentioned_or('#'), description=information)

initial_extensions = ['cogs.music', 'cogs.info', 'cogs.memes']


@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

if __name__ == "__main__":

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
            print('failed to load extension {}'.format(extension))

    credentials = utilities.load_credentials()
    bot_token = credentials['token']
    bot.run(bot_token)


