from telegram import *
from telegram.ext import *
import requests
import json
from types import SimpleNamespace
import math
import random
import time
from datetime import datetime
import pytz
from dateutil import tz

domain = "https://api.chootc.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Tham giá @chootcvn để mua, bán USDT số lượng lớn.", parse_mode=constants.ParseMode.HTML)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    message = update.message.text

    if "chốt mua" in message.lower():
        amount = float(message.split()[2].split("/")[0].replace("u",""))
        format_amount = f'{amount:,}'

        rate = int(message.split()[2].split("/")[1])
        format_rate = f'{rate:,}'

        money = amount * rate
        format_money = f'{round(money):,}'

        text = f"<b>TẠO ĐƠN MUA THÀNH CÔNG</b>\n<b>Mã giao dịch:</b> 102023151754\n<b>Số tiền:</b> {format_amount} * {format_rate} = {format_money}"

        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=constants.ParseMode.HTML)
    
    if update.message.reply_to_message:
        if "TẠO ĐƠN MUA THÀNH CÔNG" in update.message.reply_to_message.text:
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=constants.ParseMode.HTML)


app = ApplicationBuilder().token(
    "6217705988:AAEOYp5g31rkl-iWrXAGE_mo7t0f0Oz3qIo").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, messageHandler))

app.run_polling()

