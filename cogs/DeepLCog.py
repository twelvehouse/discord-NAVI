import httpx, json

import discord 
from discord.ext import commands

import json
import re

from config_manager import ConfigManager

class DeepLCog(commands.Cog):
    # コンストラクタ
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    # 翻訳を生成する
    async def generate_translation(self, text: str, target_lang: str) -> str:
        api_key = self.config.get('DEEPLX', 'api_key')
        endpoint = f"https://deeplx.missuo.ru/translate?key={api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "text": text,
            "source_lang": "auto",
            "target_lang": target_lang.upper()
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(endpoint, json=payload, headers=headers, timeout=10.0)
                res.raise_for_status()
                return res.json().get("data")
        except Exception as e:
            raise RuntimeError(f"API通信に失敗しました: {e}")

    
    # on_message イベントをリスナーに登録する
    @commands.Cog.listener()
    async def on_message(self, message):
        self.command_author = message.author

        # 送信者が BOT だった場合は無視
        if message.author.bot:
            return
        # DMchannel なら無視
        if isinstance(message.channel, discord.DMChannel):
            return
        # DEEPLX_CHANNEL_KEY が含まれていないトピックなら無視
        topic = message.channel.topic
        if topic is None or self.config.get('DEEPLX', 'channel_key') not in topic:  # トピックがないか、キーが含まれていない
            return
        else: # トピック内からregexで lang:XX を抽出してself.target_langに設定する
            lang_regex = re.compile(r'lang:(\w{2})')
            match = lang_regex.search(topic)
            if match:
                self.target_lang = match.group(1)
            else:
                self.target_lang = "JA"
        # コマンドなら無視
        if message.content.startswith(self.config.get('DISCORD', 'prefix')):
            return
        # システムメッセージなら無視
        if message.type == discord.MessageType.pins_add: # ピン留め
            return
        
        # 書き込み中ステータスに変更
        async with message.channel.typing():
            # 翻訳を生成
            try:
                response = await self.generate_translation(message.content, self.target_lang)
                # Discord 上でワンクリックでコピーできるよう、コードブロックにする
                response = f"```\n{response}\n```"
                # 2000 文字を超えていた場合は Embed で返信
                if len(response) > 2000:
                    embed = discord.Embed(title="Response", description=response, color=0xf1c40f)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"翻訳に失敗しました。エラー: {e}")

    # target_langを指定して翻訳
    @commands.hybrid_command()
    async def translate(self, ctx, target_lang: str, *, text:str):
        """
        Translate text
        """
        # thinking にする
        async with ctx.typing():
            try:
                response = await self.generate_translation(text, target_lang)
                # 2000 文字を超えていた場合は Embed で返信
                if len(response) > 2000:
                    embed = discord.Embed(title="Response", description=response, color=0xf1c40f)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(response)
            except Exception as e:
                await ctx.send(f"翻訳に失敗しました。エラー: {e}")
            
# ホットリロード時に cog を削除する
async def teardown(bot):
    await bot.remove_cog()

# Bot 本体から呼び出される
async def setup(bot):
    await bot.add_cog(DeepLCog(bot)) # MainCog クラスに bot を渡してインスタンス化、コグとして登録