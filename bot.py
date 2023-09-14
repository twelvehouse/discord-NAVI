import discord
from discord.ext import commands
import traceback

import datetime
import pytz

import asyncio
import psutil

import configparser
config = configparser.ConfigParser()

# 環境変数は .env から読み込む
from dotenv import load_dotenv
load_dotenv()

INITIAL_COGS = [
    'cogs.mainCog',
    'cogs.chatGPTCog'
]

# 設定読み込み
config.read('config/config.ini')
OWNER_ID = int(config['DISCORD']['owner_id'])   # DM 送信先のID


# 起動時DMのID格納用
DM_ID = None

# JST に変換
def jst(utc_time):
    # タイムゾーンを JST に指定
    jst_timezone = pytz.timezone('Asia/Tokyo')
    
    # JST に変換
    utc = pytz.timezone('UTC')
    utc_time = utc.localize(utc_time)   # UTC付与
    jst_time = utc_time.astimezone(jst_timezone)
    
    return jst_time

# BOT の起動時刻を取得
start_time = jst(datetime.datetime.utcnow())

# BOT のかどう時間を取得
async def get_uptime():
    # 現在の時刻を取得
    current_time = jst(datetime.datetime.utcnow())
    # 稼働時間を計算
    uptime = current_time - start_time
    # 稼働時間を整形
    uptime_hours = uptime.total_seconds() / 3600

    return uptime_hours

# DM 用メッセージを生成
async def generate_dm_message():
    # BOTの起動時間、累計稼働時間、最後のハートビート時刻を取得
    uptime_hours = await get_uptime()
    heartbeat_time = jst(datetime.datetime.utcnow()).strftime('%Y/%m/%d %H:%M:%S')

    # ついでに招待リンクも生成
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True),
        scopes=("bot", "applications.commands")
    )

    # メッセージのテンプレート
    message_template = f"-----------------------------------------------\n" \
                       f"**Wakeup Datetime:** {start_time.strftime('%Y/%m/%d %H:%M:%S')}\n" \
                       f"**Last Heartbeat:**      {heartbeat_time}\n" \
                       f"**Uptime:** {uptime_hours:.2f}h\n" \
                       f"-----------------------------------------------\n" \
                       f"[**Bot Invite Link**]({invite_link})\n" \
                       f"-----------------------------------------------"
    return message_template

# DM 送信
async def send_dm(bot):
    global MESSAGE_ID   # グローバル変数の使用を宣言
    owner = await bot.fetch_user(OWNER_ID)
    message = await owner.send(await generate_dm_message())
    MESSAGE_ID = message.id  # 送信したメッセージのIDを格納

# DM 編集
async def edit_dm(bot):
    global MESSAGE_ID  # グローバル変数の使用を宣言
    owner = await bot.fetch_user(OWNER_ID)
    while True:
        try:
            dm = await owner.create_dm()
            message = await dm.fetch_message(MESSAGE_ID)
            await message.edit(content=await generate_dm_message())

            # ついでに presence も更新
            await set_presence_uptime()
            
        except Exception as e:
            print(f"Error editing DM message: {e}")

        await asyncio.sleep(900)  # 15分ごとに編集を試行

# メモリ使用率取得
def get_status_memusage() -> str:
    mem_usage = psutil.virtual_memory().percent
    return f"MEM USAGE: {mem_usage}% "
# サーバー PING 計測
def get_status_ping() -> str:
    ping = round(bot.latency * 1000)  # Botのサーバーとのpingをミリ秒単位で取得し、小数点以下を四捨五入
    return f"PING: {ping}ms "
# BOT 稼働時間取得
async def get_status_uptime() -> str:
    uptime = await get_uptime()
    return f"UPTIME: {uptime:.2f}h "

# bot presence を UPTIME に設定する
async def set_presence_uptime():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=await get_status_uptime()))

# presense 更新
async def status_task():
    while True:
        # 各種ステータスを取得する
        activity_list = [
            get_status_memusage(),
            get_status_ping(),
            await get_status_uptime(),
        ]

        for get_status in activity_list:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=get_status))
            await asyncio.sleep(20)

# メインクラス
class MyBot(commands.Bot):
    # コンストラクタ
    def __init__(self, command_prefix):
        # インテントの生成
        intents = discord.Intents.all()
        intents.message_content = True

        # スーパークラスのコンストラクタに値を渡して実行
        super().__init__(command_prefix, intents=intents, help_command=None)

    # 終了処理
    async def shutdown(bot):
        await bot.close()

    # すべての cog をリロードする
    async def reload_extensions(self):
        # Cog を読み込み
        for cog in INITIAL_COGS:
            try:
                await bot.reload_extension(cog)
            except Exception:
                traceback.print_exc()
        await bot.tree.sync()

    # Bot の準備完了時
    async def on_ready(self):
        for cog in INITIAL_COGS:
            try:
                await bot.load_extension(cog)
            except Exception:
                traceback.print_exc()

        await bot.tree.sync()
        await bot.change_presence(activity=discord.Game(name="initialized."))

        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')

        # オーナーに DM を送信
        await send_dm(bot)
        bot.loop.create_task(edit_dm(bot))

# 実行
if __name__ == '__main__':
    bot = MyBot(command_prefix=config['DISCORD']['prefix'])
    bot.run(config['DISCORD']['token'])