import random

from discord.ext import commands


class Qaz:
    def __init__(self, bot):
        self.bot = bot
        self.filename = 'files\qaz.txt'
        self.qaz_file = open(self.filename, 'r')
        self.qaz_list = dict()

        for line in self.qaz_file:
            data = line.split()
            qaz_post = ''
            qaz_tag = ''

            for block in data:
                if block.startswith('http'):
                    qaz_post += block + ' '
                else:
                    qaz_tag += block + ' '

            self.qaz_list[qaz_tag.strip()] = qaz_post.strip()
        self.qaz_file.close()
        self.qaz_file = open(self.filename, 'a')

    @commands.group(pass_context=True, no_pm=True)
    async def qaz(self, ctx):
        """Lets you save dank qaz quotes.
            If a subcommand is not called, a random qaz quote is displayed."""

        if ctx.invoked_subcommand is None:
            tags = list(self.qaz_list.keys())
            await self.bot.say(self.qaz_list[tags[random.randrange(0, len(tags))]])

    @qaz.command(pass_context = True, no_pm = True)
    async def add(self, ctx, *msg:str):
        tag = msg[0]
        link = msg[1]
        if (tag not in list(self.qaz_list.keys())):
            print(self.qaz_file.write('\n' + link + ' ' + tag))
            self.qaz_file.flush()
            self.qaz_list[tag] = link
            await self.bot.say('Tag added successfully!')
        else:
            await self.bot.say('That tag already exists!')

    @qaz.command(name = 'list', pass_context = True, no_pm = True)
    async def _list(self, ctx):
        print(list(self.qaz_list.keys()))

def setup(bot):
    bot.add_cog(Qaz(bot))