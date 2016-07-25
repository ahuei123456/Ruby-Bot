from discord.ext import commands
from cogs.utils import utilities
from cogs.utils import checks
from cogs.utils import texttable

import asyncio, os, urllib.request

class Administrative:

    results_read = 'Here are the currently unanswered suggestions:'
    results_accepted = 'Here are the currently unfinished unanswered suggestions:'
    results_reject = 'Your request: "{0}" has been rejected for the following reason: {1}'
    results_accept = 'Your request: "{0}" has been accepted with the following comment: {1}'
    results_finish = 'Congratulations! Your request: "{0}" has been completed with the following remarks: {1}'

    error_suggestion_too_long = 'Your suggestion is too long! Please limit it to 160 characters.'
    tbl_suggest = ('ID', 'Creator', 'Suggestion', 'Status')

    code_block = '```'

    delay_del_command = 3
    delay_del_play = 1
    delay_del_announcement = 30

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self):
        """
        Displays an invite link for Ruby Bot.
        Before adding Ruby Bot to your server, please take into consideration the fact that many of Ruby Bot's features
        are developed specifically for the /r/LoveLive discord server and may not be compatible with your server.
        With that in mind, if you still wish to add Ruby Bot to your server, please go ahead.
        """
        json = utilities.load_credentials()
        await self.bot.say('Invite link: ' + json['invite_link'])

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    @checks.is_owner()
    async def nick(self, ctx, *, nickname: str=None):
        member = ctx.message.server.me
        await self.bot.change_nickname(member, nickname)

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    @checks.is_owner()
    async def clone(self, ctx):
        try:
            clonee = ctx.message.mentions[0]
            await self.bot.change_nickname(ctx.message.server.me, clonee.display_name)
            print(clonee.avatar_url)
            fname = clonee.avatar_url.split('/')
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers = {'User-Agent': user_agent,}
            edited_url= 'https://cdn.discordapp.com/avatars/' + fname[len(fname) - 3] + '/' + fname[len(fname) - 1]
            print(edited_url)
            full = os.path.join('files', 'stolen_avatars', fname[len(fname) - 1])

            request = urllib.request.Request(url=edited_url, headers=headers)
            response = urllib.request.urlopen(request)
            with open(full, 'b+w') as f:
                f.write(response.read())
            with open(full, 'rb') as fp:
                await self.bot.edit_profile(avatar=fp.read())
        except IndexError:
            with open(os.path.join('files', 'ruby.png'), 'rb') as fp:
                await self.bot.edit_profile(avatar=fp.read())
                await self.bot.change_nickname(ctx.message.server.me, None)

        await self.bot.say(':ok_hand:')


    # Suggestion commands from here onward
    @commands.command(name='suggest', pass_context=True)
    async def suggest(self, ctx, *, suggestion: str):
        """
        Suggest something for the bot!
        :param suggestion: Your suggestion.
        """
        if ctx.invoked_subcommand is None:
            suggestion = suggestion.strip()
            if len(suggestion) <= 160:
                utilities.suggest(ctx.message.author.id, suggestion)
                await self.bot.say('Suggestion "{0}" has been added successfully!'.format(suggestion))
            else:
                await self.error_long_suggestion()

    @commands.command(name='read', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _read(self, ctx):
        await self.retrieve_suggestion(ctx, 'read')

    @commands.command(name='reject', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _reject(self, ctx, *, reason: str):
        await self.update_suggestion(ctx, reason, 'reject')

    @commands.command(name='accept', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _accept(self, ctx, *, reason: str):
        await self.update_suggestion(ctx, reason, 'accept')

    @commands.command(name='accepted', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _accepted(self, ctx):
        await self.retrieve_suggestion(ctx, 'accepted')

    @commands.command(name='finish', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _finish(self, ctx, *, reason: str):
        await self.update_suggestion(ctx, reason, 'finish')

    async def update_suggestion(self, ctx, reason: str, update_type: str):
        data = reason.split()
        try:
            num = int(data[0])
            reason = ' '.join(data[1:])
            if update_type == 'reject':
                hunt = utilities.reject(num, reason)
                header = self.results_reject
            elif update_type == 'accept':
                hunt = utilities.accept(num, reason)
                header = self.results_accept
            elif update_type == 'finish':
                hunt = utilities.finish(num, reason)
                header = self.results_finish

            member = self.find_member(hunt[0])
            if member is not None:
                await self.bot.send_message(member, header.format(hunt[1], hunt[2]))
        except TypeError:
            await self.bot.whisper(self.error_invalid_id)

    async def retrieve_suggestion(self, ctx, retrieve_type):
        if retrieve_type == 'read':
            data = utilities.read()
            header = self.results_read
        elif retrieve_type == 'accepted':
            data = utilities.accepted()
            header = self.results_accepted

        await self.print_table(ctx, header, data, self.tbl_suggest, len(data), True)

    async def print_table(self, ctx, msg, data, titles, limit=12, pm=False):
        del_later = list()
        if not pm:
            del_later.append(ctx.message)
        error = msg + '\n'
        msg = None
        if len(data) <= limit:

            table = [titles]

            for row in data:
                table.append(row)

            output = texttable.print_table(table, 1994 - len(error))
            for x in range(0, len(output)):
                if x == 0:
                    error = self.code(error + output[x])
                else:
                    error = self.code(output[x])

                if pm:
                    await self.bot.whisper(error)
                else:
                    msg = await self.bot.say(error)
                    del_later.append(msg)

        else:
            error = self.code(error)
            if pm:
                await self.bot.whisper(error)
            else:
                msg = await self.bot.say(error)
                del_later.append(msg)

        await asyncio.sleep(self.delay_del_announcement)
        for msg in del_later:
            await self.bot.delete_message(msg)

    def code(self, msg):
        return self.code_block + msg + self.code_block

    def find_member(self, mid):
        mid = str(mid)

        for member in self.bot.get_all_members():
            if member.id == mid:
                return member

        return None


def setup(bot):
    bot.add_cog(Administrative(bot))