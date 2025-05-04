import os
from twitchio.ext import commands
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

TOKEN = os.getenv('TWITCH_TOKEN')  # should look like oauth:xxxxxxx
CHANNEL = os.getenv('TWITCH_CHANNEL')

# Simple bot class
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])

    async def event_ready(self):
        print(f'✅ Logged in as: {self.nick}')
        print(f'✅ Connected to channel: {CHANNEL}')

    async def event_message(self, message):
        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Hello, {ctx.author.name}! 👋')

if __name__ == '__main__':
    bot = Bot()
    bot.run()
