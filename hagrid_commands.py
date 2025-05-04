from twitchio.ext import commands
import random
from helpers import update_message_file


class HagridCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hug')
    async def hug(self, ctx):
        response = f'Hagrid: sends a big warm hug to {ctx.author.name}! 🤗'
        await ctx.send(response)
        update_message_file('Hagrid', f'sends a big warm hug to {ctx.author.name}! 🤗')

    @commands.command(name='quote')
    async def quote(self, ctx):
        quotes = [
            "What’s comin’ will come, an’ we’ll meet it when it does.",
            "I am what I am, and I’m not ashamed.",
            "Yer a wizard, Harry!",
            "Shouldn’t have said that… I should NOT have said that.",
            "Hagrid: Keeper of Keys and Grounds at Hogwarts!",
        ]
        selected = random.choice(quotes)
        response = f'Hagrid: {selected}'
        await ctx.send(response)
        update_message_file('Hagrid', selected)

    @commands.command(name='lurk')
    async def lurk(self, ctx):
        response = f'Hagrid: {ctx.author.name} has gone lurking. 🫣 We’ll keep the lantern lit!'
        await ctx.send(response)
        update_message_file('Hagrid', response)

    @commands.command(name='magic')
    async def magic(self, ctx):
        spells = [
            "casts Lumos! 💡",
            "waves wand and casts Wingardium Leviosa! 🕯️",
            "mumbles Alohomora to unlock the secrets! 🔑",
            "summons a Patronus to ward off negativity! ✨",
            "mixes a potion with a puff of smoke! 🧪",
        ]
        selected = random.choice(spells)
        response = f'Hagrid: {selected}'
        await ctx.send(response)
        update_message_file('Hagrid', selected)

# In your main bot file, after creating the ChatBot instance:
# from hagrid_commands import HagridCommands
# bot.add_cog(HagridCommands(bot))
