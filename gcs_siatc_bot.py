import discord
from discord import app_commands
import os
import logging

import dotenv
from dotenv import load_dotenv
load_dotenv()

# トークン / チャンネル読み込み
TOKEN = os.environ['DISCORD_TOKEN']
channel_id = int(os.environ['DISCORD_CHANNEL'])

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)

@client.event
async def on_ready():
    # コマンドの同期
    await tree.sync()
    print("Bot起動")

@client.event
async def on_message(message: discord.Message):
    if(message.author.bot):
        return
    
    # 設定されたチャンネルのみ
    if(message.channel.id == channel_id):
        # threadを作成　表示期間は3日　thread内は遅延設定なし
        thread:discord.Thread = await message.create_thread(name=f"{message.author.display_name}さんの質問部屋", auto_archive_duration=4320, slowmode_delay=None)
        # thread内にメッセージを送信
        await thread.send(content=f"{message.author.mention}さん、ここで質問を受けることができます！")

# 初期セットアップ用のコマンド (別に無くてもよかった)
@tree.command(name="自己紹介チャンネルの設定",description="ユーザが自己紹介をするチャンネルを設定します。（自動でチャンネルの遅延が15秒に設定されます)")
async def setup_self_introduction_channel(interaction: discord.Interaction, channel:discord.TextChannel):
    if(not interaction.permissions.administrator):
        await interaction.response.send_message(content="このコマンドはサーバー管理者のみ使用できます。", ephemeral=True)
        return
    global channel_id
    channel_id = channel.id
    # 環境変数にチャンネルIDを登録
    dotenv.set_key(dotenv.find_dotenv(), "DISCORD_CHANNEL", str(channel_id))
    # チャンネルの遅延を15秒に変更(強制)
    await channel.edit(slowmode_delay=15)
    # セットアップ完了メッセージ
    await interaction.response.send_message(content=f"チャンネルをセットアップしました: {channel.name}({channel_id})\nチャンネルの遅延を設定しました: 15秒", ephemeral=True)

# クライアント起動
client.run(token=TOKEN, log_level=logging.INFO, root_logger=True)