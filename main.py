from binance import Client
from ces import buy, sell, Quantity
import websocket
import json
import requests
import config
from Telegram import send_message, check_for_message, check_for_message_date
import time

json_message=[]
i = 0
x = 0
y = 0
ema_old_fast = 0
ema_old_slow = 0
ema_old_macd = 0
change = 0
counter = 1
last_message = ""
last_date = check_for_message_date()
position = False
up = False
macd_change = False
sold = False

ema_old = 61890
lowest = 61380
highest = 62372
sar = 62372
sar_bool = False

f = open("COIN_SAVE.txt", "r")     #Restore last Coin
symbol = f.read()
f.close()
print("Current coin:", symbol)

SOCKET = "wss://stream.binance.com:9443/ws/" + symbol.lower() + "@kline_1m"
client = Client(config.API_KEY, config.API_SECRET)

def on_open(ws):
    print('opened connection')

def on_close(ws ,a ,b):
    print('closed connection')
    send_message("Er is abgestürzt!!!")
    time.sleep(60)
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

def on_error(ws, error):
    print(error)

def save_trades():
    global trades
    f = open("trades.txt", "w")
    f.write("")
    f.close()
    f = open("trades.txt", "a")
    for a in trades:
        f.write(str(a) + "\n")
    f.close()

def telegram():
    global last_message, last_date, SOCKET, symbol, startcapital, trades, threshold, mtg, quantity, tradenum
    message = check_for_message()
    message = message.lower()
    date = check_for_message_date()
    if date != last_date:
        if message == "help" or message == "/help":
            print("help")
            send_message("Money - /wallet\nHistory - /history\nTrades(mtg) - /change_mtg\nNew Coin - /change_coin\nNew Quantity - /change_quantity\nchange percent - /change_percent\nrestart functions - /functions")
        elif message == "/functions":
            print("secret functions")
            send_message("sell everything - /sell_everything\nrestart OrderHistory - /restart_history\nrestart money - /restart_everything")
        elif message == "change coin" or message == "/change_coin":
            send_message(f"Coin: {symbol.upper()}\nWelchen Coin wollen sie?    /end")
            last_message = message
            print("change coin")
        elif last_message == "/change_coin" or last_message == "change coin" and message != "/end":
            f = open(f"{symbol.upper()}.txt", "r")
            sell(symbol.upper(), float(f.read()))
            client.cancel_order(symbol=symbol.upper())
            f.close()
            f = open("COIN_SAVE.txt", "w")
            f.write(message)
            f.close()
            quantity = Quantity(symbol, mtg)
            trades = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            tradenum = 0
            symbol = message
            SOCKET = "wss://stream.binance.com:9443/ws/" + symbol + "@kline_1m"
            last_message = ""
            send_message("Coin changed!")
        elif message == "change percent" or message == "/change_percent":
            send_message(f"Percent: {threshold}\nWie viel % wollen sie?    /end")
            last_message = message
            print("change percent")
        elif last_message == "/change_percentage" or last_message == "change percent" and message != "/end":
            threshold = float(message)
            last_message = ""
            send_message("Percent changed!")
        elif message == "restart history" or message == "/restart_history":
            print("restart history")
            with open("OrderHistory.txt", 'r+') as f:
                f.truncate(0)
            last_message = ""
            send_message("!Finished!")
        elif message == "restart trades" or message == "/restart_trades":
            print("restart trades")
            with open("trades.txt", 'r+') as f:
                f.truncate(0)
                f.write("0")
            last_message = ""
            send_message("!Finished!")
        elif message == "sell everything" or message == "/sell_everything":
            send_message(f"Are you sure to sell?    /end")
            last_message = message
            print("sell everything")
        elif last_message == "/sell_everything" or last_message == "sell everything" and message != "/end":
            f = open(f"{symbol.upper()}.txt", "r+")
            sell(symbol.upper(), float(f.read()))
            f.truncate()
            f.write("0")
            f.close()
            last_message = ""
            send_message("All sold!")
        elif message == "change quantity" or message == "/change_quantity":
            send_message(f"Quantity: {quantity}\nWie viel Quantity wollen sie?    /end")
            last_message = message
            print("change quantity")
        elif last_message == "/change_quantity" or last_message == "change quantity" and message != "/end":
            quantity = float(message)
            last_message = ""
            send_message("Quantity changed!")
        elif message == "change mtg" or message == "/change_mtg":
            send_message(f"Trades max: {mtg}\nWie viel MTG wollen sie?    /end")
            last_message = message
            print("change mtg")
        elif last_message == "/change_mtg" or last_message == "change mtg" and message != "/end":
            mtg = float(message)
            quantity = Quantity(symbol, mtg)
            last_message = ""
            quantity = Quantity(symbol, mtg)
            send_message("MTG changed!")
        elif message == "restart everything" or message == "/restart everything":
            send_message(f"How much money do you want?    /end")
            last_message = message
            print("restart money")
        elif last_message == "restart everything" or last_message == "/restart_everything" and message != "/end":
            trades = [0,0,0,0,0,0,0,0,0,0]
            tradenum = 0
            f = open(f"{symbol.upper()}.txt", "w")
            f.write("0")
            f.close()
            f = open("trades.txt", "w")
            f.write("0")
            f.close()
            f = open("USDT.txt", "w")
            f.write(message)
            f.close()
            send_message("!Finished!")
        elif message == "/wallet" or message == "wallet":
            f = open("USDT.txt", "r")
            geld = float(f.read())
            f.close()
            f = open(symbol.upper() + ".txt", "r")
            munze = float(f.read())
            f.close()
            munzeprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
            munzeprice = json.loads(munzeprice.text)
            munzeprice = float(munzeprice["price"])
            sum = (geld + (munze * float(munzeprice)))
            send_message(f"USD: {str(geld)}\n{symbol.upper()}: {str(munze)}\nCurrent Value: {str(sum)}")
        elif message == "/history" or message == "history":
            f = open("OrderHistory.txt", "r")
            send_message(f.read())
            f.close()
        elif message == "/end":
            send_message("Beendet")
            last_message = ""
        last_date = date

def on_message(ws, msg):
    global symbol, ema, ema_old, ema_old_fast, ema_old_slow, macd_line, ema_old_macd
    global position, change, sar, lowest, highest, counter, quantity
    global macd_change, i, y, x, sar_bool, buy_price, sell_price, sold
    telegram()

    #print(msg)
    msg_json = json.loads(msg)
    price = float(msg_json['k']['c'])
    is_candle_closed = msg_json['k']['x']
    price_highest = float(msg_json['k']['h'])
    price_lowest = float(msg_json['k']['l'])

    if is_candle_closed:
        if sar_bool == False and sar < price_highest:
            sar_bool = True
            sar2 = lowest

        ema_fast2 = price * (2 / 13) + ema_old_fast * (1 - (2 / 13))
        ema_slow2 = price * (2 / 27) + ema_old_slow * (1 - (2 / 27))
        macd_line2 = ema_fast2 - ema_slow2

        ema_macd2 = macd_line2 * (2 / 10) + ema_old_macd * (1 - (2 / 10))
        macd2 = macd_line2 - ema_macd2

        x += 1

        if x == 30:
            x = 0
            json_message.append(float(price))
            print(price)

            #SAR
            if price_lowest < lowest and sar_bool == True:
                lowest = price_lowest
            elif price_highest > highest and sar_bool == True:
                highest = price_highest
                counter += 1

            if price_lowest < lowest and sar_bool == False:
                lowest = price_lowest
                counter += 1
            elif price_highest > highest and sar_bool == False:
                highest = price_highest

            if sar_bool == False and sar < price_highest:
                sar_bool = True
                counter = 1
                sar = lowest
                highest = lowest
            elif sar_bool == True and sar > price_lowest:
                sar_bool = False
                counter = 1
                sar = highest
                lowest = highest

            if sar_bool:
                sar = sar + (0.02 * counter) * (highest - sar)
            elif sar_bool == False:
                sar = sar + (0.02 * counter) * (lowest - sar)
            print(f"SAR: ({sar_bool}) {sar}")

            #ema(price)
            ema = price * (2/201) + ema_old * (1-(2/201))
            ema_old = ema
            print(f"EMA200: {ema}")
            i += 1
            if i==51:
                send_message("ready")

            #MACD
            ema_fast = price * (2/13) + ema_old_fast * (1-(2/13))
            ema_old_fast = ema_fast
            ema_slow = price * (2/27) + ema_old_slow * (1-(2/27))
            ema_old_slow = ema_slow
            macd_line = ema_fast - ema_slow

            ema_macd = macd_line * (2/10) + ema_old_macd * (1-(2/10))
            ema_old_macd = ema_macd
            macd = macd_line - ema_macd
            print(f"MACD: {macd}")

        if len(json_message) >= 28 * 30:
            if ema < price:

                if macd2 > 0 and macd_change == False and ema < price_highest and y <= 4 and sold == False:
                    macd_change = True
                    y += 1
                elif macd2 < 0 and macd_change == False:
                    macd_change = True
                    y = 0
                    sold = False

                if change == 0: #Damit er zu beginn erst beim aufstieg wieder kauft
                    if macd2 > 0:
                        position = True
                    if macd2 < 0:
                        if position:
                            position = False
                            change = 1
                else:
                    if macd2 > 0 and macd_change == True:
                        if position:
                            print("Er scoutet!")
                        elif position == False:
                            if sar_bool:
                                print("buy")
                                send_message("buy")
                                quantity = Quantity(mtg=1, symbol=symbol)
                                buy(symbol, float(quantity))
                                f = open("OrderHistory.txt", "a")
                                f.write("BUY - " + str(price) + "\n")
                                f.close()
                                # limit_sell_order(sar)
                                #client.create_order(symbol=symbol.upper(), side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=quantity)
                                #set_limit_order(price) sell_order(price-sar+price)
                                buy_price = 2 * price - lowest
                                sell_price = sar2
                                position = True
                macd_change = False

    if buy_price < price or sell_price > price:
        if position:
            print("sell")
            send_message("sell")
            sell(symbol, float(quantity))
            f = open("OrderHistory.txt", "a")
            f.write("SELL - " + str(price) + "\n")
            f.close()
            position = False
            sold = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
ws.run_forever()
