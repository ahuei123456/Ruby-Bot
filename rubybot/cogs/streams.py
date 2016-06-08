from discord.ext import commands
import asyncio
from cogs.utils import twitconn

channels_text = ['139978577901780992', '172670451405946880']
channels_obj = []


class Streams:

    def __init__(self, bot):
        self.bot = bot
        self.loop = None

    async def stream(self):
        global channels_obj
        channels_obj = []
        for channel in channels_text:
            channels_obj.append(self.bot.get_channel(channel))
        if self.loop is None:
            print('Now stalking')
            self.loop = asyncio.get_event_loop()
            self.loop.create_task(self.tweet_retriever())
        else:
            print('Ending stalking')
            self.stop_loop = True
            self.loop = None

    async def tweet_retriever(self):
        await self.bot.wait_until_ready()
        self.stop_loop = False
        while not self.stop_loop:
            statuses = twitconn.stream_new_tweets()
            while len(statuses) > 0:
                status = statuses.pop(0)
                for channel in channels_obj:
                    await self.bot.send_message(channel, status)
            await asyncio.sleep(5)
