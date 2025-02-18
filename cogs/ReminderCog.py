import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os

from config_manager import ConfigManager

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
        self.owner_id = int(self.config.get('DISCORD', 'owner_id'))
        self.last_command_time = datetime.fromisoformat(self.config.get('DISCORD', 'last_command_time'))
        self.reminder_task.start()

    def save_last_command_time(self):
        self.config.set('DISCORD', 'last_command_time', self.last_command_time.isoformat())

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.last_command_time = datetime.now()
        self.save_last_command_time()

    @tasks.loop(hours=24)
    async def reminder_task(self):
        if datetime.now() - self.last_command_time > timedelta(weeks=4):
            owner = await self.bot.fetch_user(self.owner_id)
            await owner.send(f"<@{self.owner_id}> It's been 4 weeks since the last command was executed. Please keep the bot active.")

    @reminder_task.before_loop
    async def before_reminder_task(self):
        await self.bot.wait_until_ready()

async def teardown(bot):
    await bot.remove_cog()

async def setup(bot):
    await bot.add_cog(ReminderCog(bot))