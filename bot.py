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
from ast import literal_eval

domain = "https://api.chootc.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="HeroTeam", parse_mode=constants.ParseMode.HTML)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    message = update.message.text
    reply_to_message = update.message.reply_to_message

    if update.message.chat.type == "private":
        return

    if "chốt mua" in message.lower() or "chốt bán" in message.lower():
        amount = float(message.split()[2].split("/")[0].replace("usdt","").replace(",",""))
        format_amount = f'{amount:,}'

        rate = int(message.split()[2].split("/")[1])
        format_rate = f'{rate:,}'

        money = amount * rate
        format_money = f'{round(money):,}'

        type_transfer = 'sell'
        title = 'ĐƠN BÁN USDT - HEROTEAM'
        if "chốt mua" in message.lower():
            type_transfer = 'buy'
            title = 'ĐƠN MUA USDT - HEROTEAM'

        data = {
            "seller": username,
            "client": update.effective_chat.title,
            "amount": amount,
            "rate": rate,
            "total_money": money,
            "type": type_transfer,
            "debt": money
        }

        res = requests.post(f"{domain}/api/sales", data)
        code = res.json()['data']['code']

        text = f"<b>{title}</b>\n<b>{'Mã giao dịch:': <20}</b>{code}\n<b>{'Số lượng:': <24}</b>{format_amount}\n<b>{'Tỷ giá:': <28}</b>{format_rate}<b>\n{'Tổng tiền:': <24}</b>{format_money}"
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=constants.ParseMode.HTML)
    
    if reply_to_message:
        if "ĐƠN MUA USDT" in reply_to_message.text or "ĐƠN BÁN USDT" in reply_to_message.text:
            code = reply_to_message.text.split("\n")[1].split()[3]
            res = requests.get(f"{domain}/api/sales/{code}")
            data = res.json()      

            paid_usdt = 0
            paid_money = []
            banks = []
            title = 'ĐƠN BÁN USDT - HEROTEAM'

            if data['type'] == 'buy':
                title = 'ĐƠN MUA USDT - HEROTEAM'

            if data['paid_usdt']:
                paid_usdt = data['paid_usdt']

            if data['paid_money']:
                paid_money = literal_eval(data['paid_money'])

            if data['bank_name']:
                banks = literal_eval(data['bank_name'])


            if 'nhập lại' in message.lower():
                requests.put(f"{domain}/api/sales/{code}",{"paid_money": '', 'bank_name': '', "paid_usdt": 0, "debt": data['total_money']})

                bill = f"<b>{title}</b>\n<b>{'Mã giao dịch:': <20}</b>{code}\n<b>{'Số lượng:': <24}</b>{data['amount']:,}\n<b>{'Tỷ giá:': <28}</b>{data['rate']:,}<b>\n{'Tổng tiền:': <24}</b>{data['total_money']:,}"
                text = f"{bill}\n————————————————\n<b>👉 VND:\nĐã thanh toán:</b> 0\n<b>Chênh lệch:</b> {data['total_money']:,}"
                text += f"\n————————————————\n<b>👉 USDT:\nĐã thanh toán:</b> 0\n<b>Chênh lệch:</b> {data['amount']:,}"

                await context.bot.delete_message(message_id=reply_to_message.message_id, chat_id=chat_id)
                await context.bot.delete_message(message_id=update.message.message_id, chat_id=chat_id)
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=constants.ParseMode.HTML)
                return

            if 'xóa' in message.lower():
                requests.delete(f"{domain}/api/sales/{code}")
                await context.bot.delete_message(message_id=reply_to_message.message_id, chat_id=chat_id)
                await context.bot.delete_message(message_id=update.message.message_id, chat_id=chat_id)
                return
            
            if 'usdt' in message.lower():
                for i in message.split("\n"):
                    paid_usdt += float(i.replace('usdt','').replace(",",""))

                requests.put(f"{domain}/api/sales/{code}",{"paid_usdt": paid_usdt})
            
            else:
                try:
                    for i in message.split("\n"):
                        money = i.split("/")[0]
                        bank = i.split("/")[1]
                        paid_money.append(int(money.replace(",","")))
                        banks.append(bank)

                    requests.put(f"{domain}/api/sales/{code}",{"paid_money": json.dumps(paid_money), 'bank_name': json.dumps(banks)})
                except:
                    await context.bot.delete_message(message_id=update.message.message_id, chat_id=chat_id)
                    return

            paid_text = ''
            paid_total = 0
            for index, i in enumerate(paid_money):
                if index == 0:
                    paid_text += f'{i:,}'
                else:
                    paid_text += f' + {i:,}'
                paid_total += i
            if len(paid_money)>1:
                paid_text += f' = {paid_total:,}'
            if len(paid_money) == 0:
                paid_text = 0

            money_debt = data['total_money'] - paid_total
            usdt_debt = data['amount'] - paid_usdt

            requests.put(f"{domain}/api/sales/{code}",{"debt": money_debt})

            bill = f"<b>{title}</b>\n<b>{'Mã giao dịch:': <20}</b>{code}\n<b>{'Số lượng:': <24}</b>{data['amount']:,}\n<b>{'Tỷ giá:': <28}</b>{data['rate']:,}<b>\n{'Tổng tiền:': <24}</b>{data['total_money']:,}"
            text = f"{bill}\n————————————————\n<b>👉 VND:\nĐã thanh toán:</b> {paid_text}\n<b>Chênh lệch:</b> {money_debt:,}"
            text += f"\n————————————————\n<b>👉 USDT:\nĐã thanh toán:</b> {paid_usdt:,}\n<b>Chênh lệch:</b> {usdt_debt:,}"

            await context.bot.delete_message(message_id=reply_to_message.message_id, chat_id=chat_id)
            await context.bot.delete_message(message_id=update.message.message_id, chat_id=chat_id)
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=constants.ParseMode.HTML)

            if money_debt == 0 and usdt_debt == 0:
                msg = 'Giao dịch thành công. <b>HeroTeam</b> chân thành cảm ơn quý khách hàng!'
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=constants.ParseMode.HTML)


app = ApplicationBuilder().token(
    "6401609811:AAFHf746Pzq-Fv9ngogNOtUKEfrpe0EBJ5Q").build()

# app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, messageHandler))

app.run_polling()

