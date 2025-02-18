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
            if ctx.interaction:
                await ctx.interaction.response.defer(thinking=True)

            await self.bot.reload_extensions()
            await ctx.send("Reloaded.")
        except Exception as e:
            await ctx.send(f"Failed to reload. Error: {e}")

    # コグ表示
    @commands.hybrid_command()
    async def cogslist(self, ctx):
        """
        show current cog list
        """
        cog_list = [f"- {cog}" for cog in self.bot.cogs]
        await ctx.reply(f"Loaded cogs\n{chr(10).join(cog_list)}")

    # メッセージ削除
    @commands.hybrid_command()
    async def purge(self, ctx, arg):
        """
        purge messages
        """
        try:
            # ユーザーとボットのメッセージを削除する
            await ctx.channel.purge(limit=int(arg) + 1, check=lambda m: m.author == ctx.author or m.author.bot)
            return
        except Exception as e:
            await ctx.reply(f"Failed to purge messages. Error: {e}")

# ホットリロード時に cog を削除する
async def teardown(bot):
    await bot.remove_cog()

# Bot 本体から呼び出される
async def setup(bot):
    await bot.add_cog(MainCog(bot)) # MainCog クラスに bot を渡してインスタンス化、コグとして登録