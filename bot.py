import json
import math
import os
import re
import time
import glob
from revChatGPT.V3 import Chatbot
import botpy
import random

from botpy.types.message import Message

from botpy.message import DirectMessage

info = botpy.logger.info
error = botpy.logger.error


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
            info('[Command] %s', cmd + ' ' + str(add))
            output = await globals()[cmd](message, self, add)
            if len(output) < 1: return save_cfg()
            await self.api.post_message(channel_id=message.channel_id, content=output, msg_id=message.id)
            save_cfg()

    async def on_direct_message_create(self, message: DirectMessage):
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
            info('[Command] %s', cmd + ' ' + str(add))
            output = await globals()[cmd](message, self, add)
            if len(output) < 1: return save_cfg()
            await self.api.post_dms(guild_id=message.guild_id, content=output, msg_id=message.id)
            save_cfg()


async def apikey(m, s, add):
    global cfg

    if m.author.id != cfg['ownerID']: return '你没有权限'
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
    text = ''
    for data in chatbot.ask_stream(any):
        try:
            not time_now
        except:
            time_now = time.time()
        text += data
        if time.time() - time_now > cfg['Chat_stream_waitTime'] and re.search(r'(\n|。| \.|\?)', data):
            info('[chatGPT] time: %s', str(time_now) + '>' + str(time.time()))
            print(time_now, '>', time.time(), time.time() - time_now)
            time_now = time.time()
            await s.api.post_message(channel_id=m.channel_id, content=text + ' ', msg_id=m.id)
            text = ''
    return text


async def tag(m, s, any):
    system_prompt = Presets['PromptGenerator']
    chatbot = Chatbot(api_key=cfg['apikey'], system_prompt=system_prompt)
    chatbot.ask(any)


def save_cfg():
    try:
        jsonfile = open("cfg.json", "w")
        json.dump(cfg, jsonfile, indent=4)
        jsonfile.close()
    except Exception:
        error('[cfg] ', '保存cfg出现错误，已打印cfg内容')
        error('[cfg data] %s', cfg)


intents = botpy.Intents.all()
client = MyClient(intents=intents)

if not os.path.exists('cfg.json'):
    global cfg
    cfg = {}
    jsonfile = open("cfg.json", "w")
    json.dump(cfg, jsonfile, indent=4)
    jsonfile.close()
    info(f'[cfg] %s', '新建 cfg.json')
jsonfile = open("cfg.json", "r")
cfg = json.load(jsonfile)
jsonfile.close()
DefaultData = {
    'apikey': 'sk-',
    'model': 'gpt-3.5-turbo',
    'botAppID': '123456789',
    'botToken': 'AAAAABBBBB22222rrrrrwwwww84XT6s',
    'ownerID': '123456789',
    'Chat_stream_waitTime': 2,
    'Presets_directory_Path': './presets'
}
for i in DefaultData:
    try:
        not cfg[i]
    except:
        cfg[i] = DefaultData[i]
        info(f'[cfg] 初始化 %s', i)
if cfg['apikey'] == 'sk-':
    save_cfg()
    error('[cfg] ', '配置未填写,请填写 cfg.json')
    raise Exception('配置文件 没有配置 ./cfg.json')

Presets = {}
for file_path in glob.glob(os.path.join(cfg['Presets_directory_Path'], '*.txt')):
    # 打开文件并读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # 将文件内容添加到字典中
    fileName = os.path.basename(file_path).replace('.txt', '')
    cfg[fileName] = content
    info(f'[PresetsLoad] 加载预设: %s', fileName)

save_cfg()

client.run(appid=cfg['botAppID'], token=cfg['botToken'])
