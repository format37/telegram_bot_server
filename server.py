#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples/webhook_examples
# https://core.telegram.org/bots/api

import logging
import ssl
from aiohttp import web
import telebot
import asyncio
import sys
import os

SCRIPT_PATH	= '/home/format37_gmail_com/projects/telegram_bot_server/'

WEBHOOK_HOST = 'www.scriptlab.net'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = SCRIPT_PATH+'webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = SCRIPT_PATH+'webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST with www

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

app = web.Application()
bots	= []
'''
# === === === f37t1 ++

sys.path.append('/home/format37_gmail_com/projects/f37t1')
from f37t1 import bot as f37t1_bot
bot_t1	= f37t1_bot(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT)
bots.append( bot_t1 )

# Handle '/start' and '/help'
@bot_t1.message_handler(commands=['help', 'start'])
def send_welcome(message):
	bot_t1.reply_to(message,"t1")	

# Handle '/group'
@bot_t1.message_handler(commands=['group'])
def send_user(message):
	bot_t1.reply_to(message,   str(message.chat.id) )

# === === === f37t1 --
'''

# === === === calcubot ++

CALCUBOT_SCRIPT_PATH     = '/home/format37_gmail_com/projects/calcubot_python/'

sys.path.append('/home/format37_gmail_com/projects/calcubot_python')
from calcubot import calcubot_init, calcubot_about, calcubot_help, calcubot_eval, calcubot_words, calcubot_plot
calcubot	= calcubot_init(WEBHOOK_HOST,WEBHOOK_PORT,WEBHOOK_SSL_CERT, CALCUBOT_SCRIPT_PATH)
bots.append( calcubot )

CALCUBOT_WORDS = calcubot_words(CALCUBOT_SCRIPT_PATH)

@calcubot.inline_handler(func=lambda chosen_inline_result: True)
def query_text(inline_query):
	try:
		god_mode	= inline_query.from_user.id==106129214
		'''
		if inline_query.query[:5] = '/plot':
			expression = expression[5:]
		else:
			expression = inline_query.query
		'''
		answer	= calcubot_eval(True,inline_query.query,god_mode,CALCUBOT_WORDS)
		calcubot.answer_inline_query(inline_query.id, answer)
	except Exception as e:
		print(str(e))

@calcubot.message_handler(commands=['help', 'start'])
def send_help(message):
	filepath = calcubot_help(CALCUBOT_SCRIPT_PATH)
	gif = open(filepath, 'rb')
	print ( calcubot.send_animation(message.chat.id, gif, width = 776, height = 855, reply_to_message_id = str(message)) )
	
@calcubot.message_handler(commands=['about'])
def send_about(message):
	answer = calcubot_about()
	calcubot.reply_to(message, answer)

@calcubot.message_handler(commands=['cl'])
def send_user(message):
	god_mode	= message.from_user.id==106129214
	answer	= calcubot_eval(False, str(message.text)[3:],god_mode,CALCUBOT_WORDS)
	calcubot.reply_to(message, answer)

@calcubot.message_handler(commands=['plot'])
def send_plot(message):
	god_mode = message.from_user.id==106129214
	answer,filepath = calcubot_plot(CALCUBOT_SCRIPT_PATH, str(message.text)[5:],god_mode,CALCUBOT_WORDS)
	if filepath=='':
		calcubot.reply_to(message, 'Declined. '+answer)
	else:
		photo = open(filepath, 'rb')
		calcubot.send_photo(message.chat.id, photo, reply_to_message_id = str(message), caption = str(message.text)[5:])
		os.remove(filepath)
		

@calcubot.message_handler()
def send_pm(message):
	if message.chat.id==message.from_user.id:
		god_mode = message.from_user.id==106129214
		answer	= calcubot_eval(False, str(message.text),god_mode,CALCUBOT_WORDS)
		calcubot.reply_to(message, answer)
	
# === === === calcubot --

# Process webhook calls
async def handle(request):
	for bot in bots:
		if request.match_info.get('token') == bot.token:
			request_body_dict = await request.json()
			update = telebot.types.Update.de_json(request_body_dict)
			bot.process_new_updates([update])
			return web.Response()

	return web.Response(status=403)
	

app.router.add_post('/{token}/', handle)

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
