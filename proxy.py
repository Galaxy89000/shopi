import telebot
import aiohttp
import asyncio
import os
import time
import json
import re
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession, ClientTimeout


PROXY_JSON_FILE = "proxies.json"
FOOTER_HTML = "\n\n<i>🔐 Powered by <a href='https://t.me/galaxy_carders'>Galaxy Carders</a></i>"
COMMAND_PREFIXES = ["/", ".", "!", ",", "$", "#"]

# Extract proxy in format host:port:user:pass
def extract_proxy_from_text(text):
    pattern = r"([\w\.-]+:\d+:[\w\.-]+:[^\s]+)"
    match = re.search(pattern, text)
    return match.group(1) if match else None

def save_user_proxy_json(proxy: str, user_id: int):
    data = {}
    if os.path.exists(PROXY_JSON_FILE):
        with open(PROXY_JSON_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    data[str(user_id)] = proxy
    with open(PROXY_JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_proxy_json(user_id: int):
    if not os.path.exists(PROXY_JSON_FILE):
        return None
    with open(PROXY_JSON_FILE, "r") as f:
        try:
            data = json.load(f)
            return data.get(str(user_id))
        except:
            return None

def delete_user_proxy_json(user_id: int):
    if not os.path.exists(PROXY_JSON_FILE):
        return
    with open(PROXY_JSON_FILE, "r") as f:
        try:
            data = json.load(f)
        except:
            return
    if str(user_id) in data:
        del data[str(user_id)]
        with open(PROXY_JSON_FILE, "w") as f:
            json.dump(data, f, indent=4)

# Get country from IP
async def get_country_from_ip(ip: str) -> str:
    url = f"http://ip-api.com/json/{ip}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("country", "Unknown")
    except Exception:
        return "Unknown"

# Check proxy
async def check_proxy(proxy: str, timeout_sec=10, retries=2):
    try:
        host, port, user, password = proxy.strip().split(":")
    except ValueError:
        return {"status": "invalid", "proxy": proxy}

    proxy_types = ["http", "socks4", "socks5"]
    test_url = "http://httpbin.org/ip"
    headers_list = [
        {"User-Agent": "Mozilla/5.0"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        {"User-Agent": "curl/7.68.0"},
    ]

    for ptype in proxy_types:
        proxy_url = f"{ptype}://{user}:{password}@{host}:{port}"
        ip_list = []

        for attempt in range(retries):
            try:
                connector = ProxyConnector.from_url(proxy_url)
                timeout = ClientTimeout(total=timeout_sec)
                headers = headers_list[attempt % len(headers_list)]

                async with ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
                    async with session.get(test_url) as resp:
                        if resp.status == 200:
                            json_data = await resp.json()
                            ip = json_data.get("origin", "")
                            ip_list.append(ip)
                            await asyncio.sleep(1)  # Delay for rotation test
            except Exception:
                continue

        if ip_list:
            rotating = len(set(ip_list)) > 1
            final_ip = ip_list[-1]
            country = await get_country_from_ip(final_ip)

            return {
                "proxy": proxy,
                "status": "live",
                "ping": None,
                "type": ptype,
                "ip": final_ip,
                "country": country,
                "rotating": rotating
            }

    return {"proxy": proxy, "status": "dead", "ping": None, "type": None, "ip": None, "country": None, "rotating": None}

# Format result
def format_proxy_result(result, masked=True):
    if result.get("status") == "invalid":
        return "❌ <b>Invalid proxy format.</b>" + FOOTER_HTML

    proxy = result['proxy']
    if masked:
        parts = proxy.split(":")
        proxy = f"{parts[0]}:{parts[1]}:{parts[2]}:****"

    if result["status"] == "live":
        rotating = "🔄 Rotating" if result.get("rotating") else "📌 Static"
        return (
            f"✅ <b>Proxy is LIVE</b>\n"
            f"<code>{proxy}</code>\n\n"
            f"🌐 <b>IP:</b> {result['ip']}\n"
            f"🏳️ <b>Country:</b> {result['country']}\n"
            f"🔌 <b>Type:</b> {result['type']}\n"
            f"🔁 <b>Behavior:</b> {rotating}"
            + FOOTER_HTML
        )
    else:
        return f"❌ <b>Proxy is DEAD</b>\n<code>{proxy}</code>" + FOOTER_HTML

# Prefix command checker
def is_command(text, cmd):
    return any(text.lower().startswith(p + cmd) for p in COMMAND_PREFIXES)

# Register bot handlers
def register_handlers(bot):
    @bot.message_handler(func=lambda m: is_command(m.text or "", "addproxy"))
    def handle_addproxy(message):
        proxy = extract_proxy_from_text(message.text)
        if not proxy:
            bot.reply_to(message, "❌ Please send a valid proxy in this format:\n<code>host:port:user:pass</code>" + FOOTER_HTML, parse_mode="HTML")
            return
        msg = bot.reply_to(message, "⏳ <i>Checking your proxy...</i>", parse_mode="HTML")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_proxy(proxy))
        result["proxy"] = proxy

        if result["status"] == "live":
            save_user_proxy_json(proxy, message.chat.id)

        bot.edit_message_text(format_proxy_result(result), message.chat.id, msg.message_id, parse_mode="HTML")

    @bot.message_handler(func=lambda m: is_command(m.text or "", "checkproxy"))
    def handle_checkproxy(message):
        proxy = extract_proxy_from_text(message.text)
        if not proxy:
            bot.reply_to(message, "❌ Please send a valid proxy in this format:\n<code>host:port:user:pass</code>" + FOOTER_HTML, parse_mode="HTML")
            return
        msg = bot.reply_to(message, "⏳ <i>Checking proxy status...</i>", parse_mode="HTML")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_proxy(proxy))
        result["proxy"] = proxy

        bot.edit_message_text(format_proxy_result(result), message.chat.id, msg.message_id, parse_mode="HTML")

    @bot.message_handler(func=lambda m: is_command(m.text or "", "myproxy"))
    def handle_myproxy(message):
        proxy = get_user_proxy_json(message.chat.id)
        if not proxy:
            bot.reply_to(message, "📭 <i>No proxy saved.</i>" + FOOTER_HTML, parse_mode="HTML")
            return
        msg = bot.reply_to(message, "⏳ <i>Checking your saved proxy...</i>", parse_mode="HTML")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_proxy(proxy))
        result["proxy"] = proxy

        bot.edit_message_text(format_proxy_result(result), message.chat.id, msg.message_id, parse_mode="HTML")

    @bot.message_handler(func=lambda m: is_command(m.text or "", "delproxy"))
    def handle_delproxy(message):
        delete_user_proxy_json(message.chat.id)
        bot.reply_to(message, "🗑️ <b>Your proxy has been removed.</b>" + FOOTER_HTML, parse_mode="HTML")
