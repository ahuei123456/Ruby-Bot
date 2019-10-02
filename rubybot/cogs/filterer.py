from discord.ext import commands
from dataclasses import dataclass
from enum import Enum
from typing import Pattern
from utils import checks
import discord
import logging
import os
import pickle
import re


save_path = os.path.join(os.getcwd(), 'data', 'filters.json')


class Action(Enum):
    CHANNEL = 0
    DM = 1


@dataclass
class Filter:
    name: str
    check: Pattern
    response: str
    action: Action

    def get_embed(self):
        embed = discord.Embed(title=self.name)
        embed.add_field(name='Regex', value=self.check.pattern)
        embed.add_field(name='Response', value=self.response)
        embed.add_field(name='Target', value='Channel')

        return embed


class Filterer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._load_filters()

    def _load_filters(self):
        try:
            self.filters = pickle.load(open(save_path, 'rb'))
        except FileNotFoundError:
            self.filters = dict()

    def _save_filters(self):
        pickle.dump(self.filters, open(save_path, 'wb'))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            content = message.content

            for f in self.filters.values():
                if f.check.search(content) is not None:
                    if f.action == Action.CHANNEL:
                        await message.channel.send(f.response)
                    elif f.action == Action.DM:
                        await message.author.send(f.response)

    @commands.group()
    async def filter(self, ctx):
        pass

    @filter.command()
    @checks.is_owner()
    async def register(self, ctx, name, check, response):
        f = Filter(name, re.compile(check), response, Action.CHANNEL)
        self.filters[name] = f

        embed = f.get_embed()
        await ctx.send(content='Registered new filter!', embed=embed)

        self._save_filters()

    @filter.command()
    @checks.is_owner()
    async def delete(self, ctx, name):
        if name in self.filters:
            self.filters.pop(name)
            await ctx.send(f'Deleted filter {name}')
            self._save_filters()
        else:
            await ctx.send(f'Could not find filter {name}')

    @filter.command()
    async def list(self, ctx):
        msg = ''
        for name, f in self.filters.items():
            msg += f'{name}: {f.check.pattern} -> {f.response}\n'

        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Filterer(bot))
