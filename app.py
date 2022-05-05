from flask import Flask, request, Response
import requests
import re  # Regular expression operations
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("API_TOKEN")

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        msg = request.get_json()
        chat_id, symbol, quantity = parse_messages(msg)
        if not chat_id:
            pass
            return Response("ok", status=200)
        elif not symbol:
            send_message(chat_id, "wrong data")
            return Response("ok", status=200)
        elif symbol == '/start':
            send_message(chat_id, "Instruction: /currency quantity(optional). F.e: /usd 100\n\
                         Инструкция: /валюта количество(по желанию). Например: /usd 100\n\
                         Instruksiya: /valyuta raqam(xohishiga qarab). Masalan: /usd 100")
            return Response("ok", status=200)
        elif int(quantity) > 10000:
            send_message(chat_id, "Ты чо слишком богатый чтоли? По меньше введи")
            return Response("ok", status=200)
        else:
            price, c = get_currency(symbol)
            try:
                float(price)
                if c == "USD":
                    price = f"{quantity}($) 🇺🇸 𝘋𝘖𝘓𝘓𝘈𝘙  ⇋  {(float(price) * int(quantity)):,} 🇺🇿 𝘚𝘜𝘔"
                    send_message(chat_id, price)
                elif c == "RUB":
                    price = f"{quantity}(₽) 🇷🇺 𝘙𝘜𝘉𝘓𝘌  ⇋  {(float(price) * int(quantity)):,} 🇺🇿 𝘚𝘜𝘔"
                    send_message(chat_id, price)
                elif c == "EUR":
                    price = f"{quantity}(€) 🇪🇺 𝘌𝘜𝘙𝘖  ⇋  {(float(price) * int(quantity)):,} 🇺🇿 𝘚𝘜𝘔"
                    send_message(chat_id, price)
            except (Exception,):
                send_message(chat_id, price)
            return Response("ok", status=200)
    else:
        return 'EXCHANGE RATE'


def parse_messages(message):
    try:
        chat_id = message["message"]["chat"]["id"]
        txt = message["message"]['text']
        # pattern = r'/[a-zA-Z]{2,5}'
        pattern = r'(/[a-zA-Z]{3,5}\s?)(\s\d{1,})?$'
        ticker = re.findall(pattern, txt)  # re.findall(pattern, string) | return [...]
        quantity = None
        if ticker[0][0].strip() in ("/usd", "/rub", "/eur", "/start"):
            if not ticker[0][1]:
                symbol = ticker[0][0]  # /usd
                quantity = 1
            else:
                symbol = ticker[0][0]
                quantity = ticker[0][1]
        else:
            symbol = ""
        return chat_id, symbol, quantity
    except (Exception,):
        return "", "", ""


def send_message(chat_id, text='bla-bla-bla'):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    r = requests.post(url, json=payload)
    return r


def get_currency(currency):
    try:
        bank_url = "https://nbu.uz/en/exchange-rates/"
        bank_data = requests.get(bank_url)
        bank_soup = BeautifulSoup(bank_data.content, "html.parser")
        table = bank_soup.find("table")
        price = None
        c = None
        if currency.strip() == "/usd":
            price = table.findAll("td")[1].text
            c = "USD"
        elif currency.strip() == "/eur":
            price = table.findAll("td")[5].text
            c = "EUR"
        elif currency.strip() == "/rub":
            price = table.findAll("td")[9].text
            c = "RUB"
        return price, c
    except (Exception,):
        return "Incorrect currency"


if __name__ == '__main__':
    app.run()

# https://api.telegram.org/bot5235037221:AAGp3UGiqGKXnHc8PsGIWrBiRWD17JgipUw/setWebhook?url=https://cmc-app-1803.herokuapp.com/
