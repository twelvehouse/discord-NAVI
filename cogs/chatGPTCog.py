from revChatGPT.V1 import AsyncChatbot

import discord 
from discord.ext import commands

import configparser
import json

from os import environ


# config 管理
def read_config():
    config = configparser.ConfigParser()
    config.read("config/config.ini")
    return config

def write_config(config):
    with open("config/config.ini", "w") as configfile:
        config.write(configfile)

def get_json_value(json_raw: str, key):
    # json かどうか確認
    if json_raw.startswith("{"):
        dict = json.loads(json_raw)
        return dict[key]
    else:
        return None


CHAT_CHANNEL_KEY = read_config()['ENVIROMENT']['channel_key']
PREFIX = read_config()['DISCORD']['prefix']

class chatGPTCog(commands.Cog):
    # コンストラクタ
    def __init__(self, bot):
        self.bot = bot
        self.chatbot = self.get_chatbot()

    # AsyncChatBot の初期化
    def get_chatbot(self) -> AsyncChatbot:
        # config からトークンを取得
        token = read_config()['CHATGPT']['token']

        # 環境変数からリバースプロキシのURLが読み込まれているか確認
        base_url = environ.get('CHATGPT_BASE_URL')
        print(f"CHATGPT_BASE_URL: {base_url}")

        chatbot = AsyncChatbot(
            config={ "access_token": token },
            conversation_id=read_config()['CHATGPT']['conversation_id'],
        )
        print(f"Successfully initialized chatbot.")

        return chatbot

    # 返答を生成する
    async def generate_response(self, prompt: str) -> str:
        async for response in self.chatbot.ask(prompt):
            message = response['message']
        return message

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
        # チャットチャンネルでなければ無視
        topic = message.channel.topic
        if topic is None or CHAT_CHANNEL_KEY not in topic:  # トピックがないか、キーが含まれていない
            return
        # コマンドなら無視
        if message.content.startswith(PREFIX):
            return
        # システムメッセージなら無視
        if message.type == discord.MessageType.pins_add: # ピン留め
            return
        
        # 書き込み中ステータスに変更
        async with message.channel.typing():
            # Chatbot による返答の取得を試みる
            try:
                # 取得
                response = await self.generate_response(message.content)
                # 2000 文字を超えていた場合は Embed で返信
                if len(response) > 2000:
                    embed = discord.Embed(title="Response", description=response, color=0xf1c40f)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(response)
            except Exception as e:
                # エラーが発生した場合はエラーを返信する
                error_msg = f"```json\n" + f"{e}\n```"
                embed = discord.Embed(title="Error", description=error_msg, color=0xe74c3c)
                await message.channel.send(embed=embed)

    # リセット
    @commands.hybrid_command()
    async def reset(self, ctx):
        """
        Reset Conversation
        """
        # thinking にする
        async with ctx.typing():
            try:
                # 会話をリセットして、古い会話を削除する
                self.chatbot.reset_chat()
                # 削除を試みる、できなくても何もしない
                try:
                    await self.chatbot.delete_conversation(read_config()['CHATGPT']['conversation_id'])
                except:
                    print(f"conversation_id: {read_config()['CHATGPT']['conversation_id']} is not found.")
                    pass

                # 新しく会話を開始して、conversation_id を更新する
                init_prompt = read_config()['CHATGPT']['init_prompt'] # 初期プロンプトを取得
                await self.generate_response(init_prompt)
                conversation_id = self.chatbot.conversation_id  # 新しい conversation_id を取得
                await self.chatbot.change_title(conversation_id, "NAVI chat")   # 会話のタイトルを変更
                print(f"new conversation_id: {conversation_id}")
                # config を更新する
                config = read_config()
                config['CHATGPT']['conversation_id'] = conversation_id
                write_config(config)

                await ctx.reply("Conversation has been reset.")
            except Exception as e:
                # エラーが発生した場合はエラーを返信する
                error_msg = f"```json\n" + f"{e}\n```"
                embed = discord.Embed(title="Error", description=error_msg, color=0xe74c3c)
                await ctx.reply(embed=embed)

    # token を更新する
    @commands.hybrid_command()
    async def update_token(self, ctx, arg):
        """
        Update Chatbot access_token
        """
        # arg(json) から token を取り出す
        token = get_json_value(arg, "accessToken")
        # config を更新する
        config = read_config()
        config['CHATGPT']['token'] = token
        write_config(config)
        # chatbot の再初期化
        self.chatbot = self.get_chatbot()
        await ctx.reply("Chatbot access_token has been updated.")

    # conversation_id を更新する
    @commands.hybrid_command()
    async def update_conversation(self, ctx, arg):
        """
        Update Chatbot conversation_id
        """
        # config を更新する
        config = read_config()
        config['CHATGPT']['conversation_id'] = arg
        write_config(config)
        # chatbot の再初期化
        self.chatbot = self.get_chatbot()
        await ctx.reply("Chatbot conversation_id has been updated.")

# ホットリロード時に cog を削除する
async def teardown(bot):
    await bot.remove_cog()

# Bot 本体から呼び出される
async def setup(bot):
    await bot.add_cog(chatGPTCog(bot)) # MainCog クラスに bot を渡してインスタンス化、コグとして登録