#include files
import discord
from discord.ext import commands
import asyncio
import logging
import random
import aiohttp
from time import localtime, strftime
from datetime import date
import json
import urllib.request
import simplejson
from io import StringIO
from apiclient.discovery import build

#logger for the internal console, the discordAPI, and Snapbot itself.
logger = logging.getLogger('pizzabot_console')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

logger2 = logging.getLogger('discord')
logger2.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='pizzabot_discordAPI.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger2.addHandler(handler)

logger3 = logging.getLogger('snapbot')
logger3.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='pizzabot_logfile.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger3.addHandler(handler)

#init Snapbot
print('Pizzabot Loading...')
logger3.debug("Pizzabot Loading...")

#init bot
bot = commands.Bot(command_prefix="(>", description="lemme order a number 9...")
aiosession = aiohttp.ClientSession(loop=bot.loop)

owner_list = ["184013824850919425", "226441820467494914"]

events = ["was robbed by a angry mob","was taken to jail for taking illegal drugs","was taken to jail for murdering a guy.","was too busy being in his house playing games","was fired","was killed","had to go to the hospital for a life-threatening condition","was murdered by a shotgunner at point blank"]

config = {}
   
with open('config.json') as json_config_file:
     config = json.load(json_config_file)

preperationtime = float(config["preperationtime"])
cooktime = float(config["cooktime"])
delivertime = float(config["delivertime"])

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )
        
#ready event.
@bot.event
async def on_ready():
  print('Logged in!')
  print('---------')
  print('Name: ' + bot.user.name)
  print('ID: ' + bot.user.id)
  print('---------')
  print('Pizzabot Loaded.')
  print('---------')
  print('To invite to your server use')
  print('https://discordapp.com/api/oauth2/authorize?client_id=' + bot.user.id + '&scope=bot&permissions=0')
  print('---------')

#event on message.
@bot.event
async def on_message(message):       
  await bot.process_commands(message)
  
@bot.event
async def on_message_edit(before, after):
  await bot.process_commands(after)
  
@bot.command(pass_context=True, no_pm=True)
async def order(ctx, *, msgstr=None):
  """Pizza - Orders a pizza."""
  message = ctx.message
  author = message.author
  msgstr += " pizza"
  await response(message,"Order Received!","{0.mention}, Your order has been recived by the bot. Please wait for {1} for your pizza to be prepared.".format(author,display_time(preperationtime)))
  await asyncio.sleep(preperationtime)
  await response(message,"Cooking Started!","{0.mention}, Your pizza is now in the oven! Please wait for {1} for your pizza to be cooked.".format(author,display_time(cooktime)))
  await asyncio.sleep(cooktime)
  await response(message,"Delivering Pizza!","{0.mention}, Your pizza is now being delevered to you! Please wait for {1} for your pizza to be delivered.".format(author,display_time(delivertime)))
  await asyncio.sleep(delivertime)
  apikey = open('apikey.txt', 'r')
  key = apikey.readline()
  apikey.close()
  cxid = open('cxid.txt', 'r')
  id = cxid.readline()
  cxid.close()
  service = build("customsearch", "v1",developerKey=key)
  res = service.cse().list(q=msgstr,cx=id,searchType='image',num=1,imgType='photo',fileType='png',safe= 'off').execute()
 
  if not 'items' in res:
     await response(message,"Order Error","Sorry {0.mention}, but the delivery guy {1} while trying to deliver your pizza. sorry about that.".format(author, random.choice(events)))
  else:
     for item in res['items']:
       await response_ex(message,"Your pizza is here, enjoy!","{0.mention}, your pizza is here, enjoy!".format(author),item['link'])
	   
@bot.command(pass_context=True, no_pm=True)
async def refund(ctx):
  """Pizza - Refunds an order"""
  message = ctx.message
  author = message.author
  await response(message,"No Refunds","Sorry {0.mention}, there are no refunds. :(".format(author))
  
@bot.command(pass_context=True, no_pm=True)
async def avatar(ctx, url=None):
  """Mods - Changes the bot's avatar. Must be an attachment. (Bot Owners Only)"""
  message = ctx.message
  
  if user_owner(message):
        if message.attachments:
           thing = message.attachments[0]['url']
        else:
           await response(message, "Avatar", "Please upload your avatar in a attachment.")
           return

        try:
           with aiohttp.Timeout(10):
            async with aiosession.get(thing) as res:
                 await bot.edit_profile(avatar=await res.read())
                 await response(message, "Avatar", "Avatar Changed.")
        except Exception as e:
           await response(message, "Avatar", "Unable to change avatar.")
  
async def response(message, mtitle, content):
  await bot.send_typing(message.channel)
  em = discord.Embed(title=mtitle, description=content, colour=0x7ED6DE) 
  em.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)
  await bot.send_message(message.channel, embed=em)
  
async def response_ex(message, mtitle, content, image):
  await bot.send_typing(message.channel)
  em = discord.Embed(title=mtitle, description=content, colour=0x7ED6DE) 
  em.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)
  em.set_image(url=image)
  await bot.send_message(message.channel, embed=em)
  
def user_owner(message):
  author = message.author
  if author.id in str(owner_list):
        return True
  else:
        return False

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

print('Connecting...')
logger3.debug("Pizzabot Connecting...")
try:
 file = open('token.txt', 'r') 
 bot.run(file.readline())
 file.close()
 logger3.debug("Pizzabot Connected!")
except Exception as e:
 logger3.debug("Pizzabot failed to connect with Discord!")
except:
 bot.logout()
