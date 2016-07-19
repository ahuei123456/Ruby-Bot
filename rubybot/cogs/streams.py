from discord.ext import commands
import asyncio
from cogs.utils import twitconn
from cogs.utils import checks
import json
import os
from discord.errors import Forbidden

channels_text = ['139978577901780992', '172670451405946880']
channels_obj = []

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

        print(stalk)

        twitconn.init_stream(stalk)

        @bot.event
        async def on_ready():
            print('Ready')
            await self.stream()

        @bot.event
        async def on_resumed():
            print('Resumed')
            await self.reboot_stream()

    def get_stalks(self):
        return list(self.destinations['destinations'].keys())

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
            statuses = twitconn.stream_new_tweets()
            while len(statuses) > 0:
                fstatus = statuses.pop(0)
                status = fstatus[1]
                id = fstatus[0]

                targets = self.destinations['destinations']
                try:
                    channels = targets[id]
                except KeyError:
                    continue

                for channel in channels:
                    if channel in self.destinations['blacklist']:
                        continue
                    try:
                        send = self.bot.get_channel(channel)
                        await self.bot.send_message(send, status)
                    except Exception as e:
                        print(channel)
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

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def stalk(self, ctx, user):
        channel = ctx.message.channel.id
        self.add_channel(user, channel)
        await self.bot.say('Now stalking ' + user + ' in channel ' + ctx.message.channel.name + '!')
        await self.reboot_stream()

    async def kill_stream(self):
        twitconn.kill_stream()

    async def restart_stream(self):
        twitconn.restart_stream(self.get_stalks())

    async def reboot_stream(self):
        twitconn.kill_stream()
        twitconn.restart_stream(self.get_stalks())

    def add_channel(self, twitter_id, channel_id):
        try:
            channels = self.destinations['destinations'][twitter_id]
            if channel_id not in channels:
                channels.append(channel_id)
        except KeyError:
            channels = [channel_id, ]
            self.destinations['destinations'][twitter_id] = channels

        path = os.path.join(os.getcwd(), 'files', 'tweets.json')
        with open(path, 'r+') as f:

            f.seek(0)  # <--- should reset file position to the beginning.
            json.dump(self.destinations, f, indent=4)



def setup(bot):
    bot.add_cog(Streams(bot))