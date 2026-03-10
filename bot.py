from SmartApi import SmartConnect
import pyotp
import requests
import time
import feedparser
import os

API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
PIN = os.getenv("PIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# -------------------
# ANGEL ONE LOGIN
# -------------------

smart=SmartConnect(api_key=API_KEY)

totp=pyotp.TOTP(TOTP_SECRET).now()

data=smart.generateSession(CLIENT_ID,PIN,totp)

print("Angel One Login Successful")

# -------------------
# TELEGRAM SETTINGS
# -------------------

BOT_TOKEN="8766217586:AAHvA5p9hOJbD7erslSmMXje6-E18RhNNlY"
CHAT_ID="5052728626"

def send_telegram(msg):

    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data={
        "chat_id":CHAT_ID,
        "text":msg
    }

    requests.post(url,data=data)

# -------------------
# GET NIFTY PRICE
# -------------------

def get_nifty():

    data=smart.ltpData(
        exchange="NSE",
        tradingsymbol="NIFTY",
        symboltoken="26000"
    )

    return data["data"]["ltp"]

# -------------------
# GET BANKNIFTY
# -------------------

def get_banknifty():

    data=smart.ltpData(
        exchange="NSE",
        tradingsymbol="BANKNIFTY",
        symboltoken="26009"
    )

    return data["data"]["ltp"]

# -------------------
# ATM STRIKE
# -------------------

def get_atm(price):

    return round(price/50)*50

# -------------------
# SIGNAL LOGIC
# -------------------

last_signal=None

def check_signal(start,current):

    global last_signal

    move=current-start

    strike=get_atm(current)

    if move>=30 and last_signal!="CE":

        msg=f"""
🚀 NIFTY BREAKOUT

BUY CE
Strike : {strike}
Spot : {current}

SL : 20
Target : 40-60
"""

        send_telegram(msg)

        last_signal="CE"

    elif move<=-30 and last_signal!="PE":

        msg=f"""
🔻 NIFTY BREAKDOWN

BUY PE
Strike : {strike}
Spot : {current}

SL : 20
Target : 40-60
"""

        send_telegram(msg)

        last_signal="PE"

# -------------------
# MARKET NEWS
# -------------------

last_news=""

def market_news():

    global last_news

    url="https://www.moneycontrol.com/rss/MCtopnews.xml"

    feed=feedparser.parse(url)

    news=feed.entries[0].title

    if news!=last_news:

        last_news=news

        send_telegram(f"""
🔥 MARKET NEWS

{news}
""")

# -------------------
# MAIN BOT LOOP
# -------------------

print("BOT RUNNING...")

send_telegram("🤖 NIFTY SIGNAL BOT STARTED")


while True:

    try:

        start_price=get_nifty()

        print("Start Price:",start_price)

        time.sleep(300)

        current_price=get_nifty()

        print("Current Price:",current_price)

        check_signal(start_price,current_price)

        bank=get_banknifty()

        print("BankNifty:",bank)

        market_news()

    except Exception as e:

        print("Error:",e)

        time.sleep(10)


