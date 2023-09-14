import discord 
from discord.ext import commands

class MainCog(commands.Cog):
    # コンストラクタ
    def __init__(self, bot):
        self.bot = bot

    # Cog のホットリロード
    @commands.hybrid_command()
    async def reload(self, ctx):
        """hot reload"""
        try:
            await self.bot.reload_extensions()
            await ctx.reply("Reloaded.")
        except Exception as e:
            await ctx.reply(f"Failed to reload. Error: {e}")

    # コグ表示
    @commands.hybrid_command()
    async def cogslist(self, ctx):
        """
        show current cog list
        """
        loaded_cogs = [cog for cog in self.bot.cogs]
        await ctx.reply(f"Loaded cogs: {', '.join(loaded_cogs)}")

    # メッセージ削除
    @commands.hybrid_command()
    async def purge(self, ctx, arg):
        """
        purge messages
        """
        try:
            await ctx.channel.purge(limit=int(arg) + 1, check=lambda m: m.author == ctx.author)
            return
        except Exception as e:
            await ctx.reply(f"Failed to purge messages. Error: {e}")

# ホットリロード時に cog を削除する
async def teardown(bot):
    await bot.remove_cog()

# Bot 本体から呼び出される
async def setup(bot):
    await bot.add_cog(MainCog(bot)) # MainCog クラスに bot を渡してインスタンス化、コグとして登録