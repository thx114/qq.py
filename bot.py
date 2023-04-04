import json
import math
import os
import re
import time

from revChatGPT.V3 import Chatbot
import botpy
import random
from botpy import BotAPI
from botpy.types.message import Message
from config import *
from botpy.message import DirectMessage


class MyClient(botpy.Client):
    async def on_message_create(self, message: Message):
        msg = str(message.content)
        if ' /' in msg or msg.startswith('/'):
            msg = re.match(r".*(/[\S\s]+)", msg)[1]
            try:
                cmd = re.match(r"/(\S+)", msg)[1]
            except:
                return
            try:
                add = re.match(r"/\S+\s([\s\S]*)", msg)[1]
            except:
                add = 0
            print('指令:', cmd, add)
            output = await globals()[cmd](message, self, add)
            if len(output) < 1 : return save_cfg()
            await self.api.post_message(channel_id=message.channel_id, content=output, msg_id=message.id)
            save_cfg()

    async def on_direct_message_create(self, message: DirectMessage):
        msg = str(message.content)
        if ' /' in msg or msg.startswith('/'):
            msg = re.match(r".*(/[\S\s]+)", msg)[1]
            print(msg)
            try:
                cmd = re.match(r"/(\S+)", msg)[1]
            except:
                return
            try:
                add = re.match(r"/\S+\s([\s\S]*)", msg)[1]
            except:
                add = 0
            print('指令:', cmd, add)
            output = await globals()[cmd](message, self, add)
            if len(output) < 1: return save_cfg()
            await self.api.post_dms(guild_id=message.guild_id, content=output, msg_id=message.id)
            save_cfg()


async def apikey(m, s, add):
    if m.author.id != owner_id:return '你没有权限'
    global cfg
    match = re.match(r'(sk-\w{6})(.*)', cfg['apikey'])
    left = match[1]
    right = match[2]
    if add == 0:
        return left + re.sub(r'\w', random.choice('*'), right)
    elif len(add) > 8:
        if add.startswith('sk-'):
            cfg['apikey'] = add
            return 'apikey设置为' + left + re.sub(r'\w', random.choice('*'), right)
        else:
            return '输入不合法'
    else:
        return '输入不合法'


async def chat(m, s, any):
    chatbot = Chatbot(api_key=cfg['apikey'])
    after_time = cfg['after_time']
    text=''
    for data in chatbot.ask_stream(any):
        try:not time_now
        except:time_now = time.time()
        text += data
        if time.time() - time_now > after_time and re.search(r'(\n|。| \.|\?)',data):
            print(time_now,'>',time.time(),time.time()-time_now)
            time_now = time.time()
            await s.api.post_message(channel_id=m.channel_id, content=text+' ', msg_id=m.id)
            text = ''

    return text


def save_cfg():
    try:
        jsonfile = open("cfg.json", "w")
        json.dump(cfg, jsonfile, indent=4)
        jsonfile.close()
    except Exception:
        print(cfg)
        print('保存cfg出现错误，已打印cfg内容')


intents = botpy.Intents.all()
client = MyClient(intents=intents)

if not os.path.exists('cfg.json'):
    global cfg
    cfg = {}
    jsonfile = open("cfg.json", "w")
    json.dump(cfg, jsonfile, indent=4)
    jsonfile.close()
jsonfile = open("cfg.json", "r")
cfg = json.load(jsonfile)
jsonfile.close()
for i in ['apikey', 'userData', 'mode', 'after_time']:
    try:
        not cfg[i]
    except:
        cfg[i] = DefaultData[i]
        print('初始化', i, '=>', cfg[i])
save_cfg()

client.run(appid=bot_id, token=bot_key)
