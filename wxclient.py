# login.py
from wxpy import *
from wechat_sender import *

bot = Bot(cache_path=True)
print("here")
# friend = bot.friends().search('honey')[0]
# print(friend)
group = bot.groups().search('搞')[0]

listen(bot, token='test', receivers=[group])
