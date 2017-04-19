from discord.ext import commands
import asyncio
from cogs.utils import twitconn
from cogs.utils import checks
from discord.errors import Forbidden, InvalidArgument
import json, os, twitutils, linkutils, discordutils


class Streams:

    bot = None

    def __init__(self, bot):
        self.bot = bot
        self.loop = None
        self.destinations = None

        path = os.path.join(os.getcwd(), 'files', 'tweets.json')
        with open(path) as f:
            self.destinations = json.load(f)

        stalk = self.get_stalks()

        twitconn.init_stream(stalk)

        @bot.event
        async def on_ready():
            print('Ready')
            await self.stream()

        @bot.event
        async def on_resumed():
            print('Resumed')
            await self.reboot_stream()

    async def stream(self):
        if self.loop is None:
            await self.start()
        else:
            await self.reboot_stream()

    async def start(self):
        print('Now stalking')
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.tweet_retriever())

    async def end(self):
        print('Ending stalking')
        self.stop_loop = True
        self.loop.stop()
        self.loop = None

    async def tweet_retriever(self):
        print('kek')
        await self.bot.wait_until_ready()
        self.stop_loop = False
        while not self.stop_loop:
            if not twitconn.poster.running:
                print('Disconnected')
                await self.reboot_stream()
                print('Reconnected')
                await asyncio.sleep(20)
                continue
            statuses = twitconn.stream_new_tweets()
            while len(statuses) > 0:
                fstatus = statuses.pop(0)
                id = str(fstatus.user.id)

                #status = twitconn.encode_status(fstatus)
                status = discordutils.encode_status(fstatus)

                targets = self.destinations['destinations']
                try:
                    channels = targets[id]
                except KeyError:
                    continue

                if channels == None:
                    continue

                for channel in channels:
                    if channel in self.destinations['blacklist']:
                        continue
                    try:
                        send = self.bot.get_channel(channel)
                        await self.bot.send_message(send, embed=status)
                    except Forbidden as e:
                        print(send.name)
                        print(e)
                    except InvalidArgument as e:
                        print(send)
                        print(e)
            await asyncio.sleep(5)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def reboot(self):
        print('command????')
        await self.bot.say('Attempting to restart stream!')
        await self.kill_stream()
        await self.bot.say('Stream killed!')
        await self.bot.say('Restarting stream...')
        await asyncio.sleep(60)
        await self.restart_stream()
        await self.bot.say('Restart successful...?')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def kill(self):
        await self.bot.say('Killing stream...')
        await self.kill_stream()
        await self.bot.say('Stream killed!')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def restart(self):
        await self.bot.say('Restarting stream...')
        await self.restart_stream()
        await self.bot.say('Stream started!')

    @commands.group(hidden=True, pass_context=True, invoke_without_command=True)
    @checks.is_owner()
    async def stalk(self, ctx, id):
        channel = ctx.message.channel.id
        user = twitutils.get_user(twitconn.api_twitter, id)
        #user = twitconn.get_user(id)
        if self.add_channel(user, channel):
            await self.bot.say('Added user {} to channel {} stalk queue!'.format(user.screen_name, ctx.message.channel.name))
        else:
            await self.bot.say('Added user {} to channel {} unfollow queue!'.format(user.screen_name, ctx.message.channel.name))

    @stalk.command(name='list', pass_context=True, hidden=True)
    async def slist(self, ctx):
        channel = ctx.message.channel.id

        stalks = []

        for key in self.get_stalks():
            channels = self.destinations['destinations'][key]

            if channel in channels:
                stalks.append(key)

        if len(stalks):
            await self.bot.say('Stalked twitter accounts on this channel: ' + str(stalks))
        else:
            await self.bot.say('This channel is not stalking any twitter accounts.')

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def blacklist(self, ctx):
        channel = ctx.message.channel.id
        if not self.blacklist_channel(channel):
            await self.bot.say("Now blacklisting this channel.")
        else:
            await self.bot.say("No longer blacklisting this channel.")

    async def kill_stream(self):
        print('killing stream')
        twitconn.kill_stream()

    async def restart_stream(self):
        print('restarting stream')
        twitconn.restart_stream(self.get_stalks())

    async def reboot_stream(self):
        print('rebooting stream')
        twitconn.kill_stream()
        twitconn.restart_stream(self.get_stalks())

    def add_channel(self, user, channel_id):
        twitter_id = user.id_str
        try:
            channels = self.destinations['destinations'][twitter_id]
            if channel_id in channels:
                channels.remove(channel_id)
                self.update_json()
                return False
            channels.append(channel_id)
        except KeyError:
            channels = [channel_id, ]
            self.destinations['destinations'][twitter_id] = channels

        self.update_json()

        return True

    def blacklist_channel(self, channel_id):
        try:
            channels = self.destinations['blacklist']
            if channel_id in channels:
                channels.remove(channel_id)
                self.update_json()
                return True
            channels.append(channel_id)
        except KeyError:
            channels = [channel_id, ]
            self.destinations['blacklist'] = channels

        self.update_json()

        return False

    def update_json(self):
        path = os.path.join(os.getcwd(), 'files', 'tweets.json')
        with open(path, 'w') as f:
            f.seek(0)  # <--- should reset file position to the beginning.
            json.dump(self.destinations, f, indent=4)

    def get_stalks(self):
        return list(self.destinations['destinations'].keys())

def setup(bot):
    bot.add_cog(Streams(bot))