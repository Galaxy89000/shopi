# b3.py
from telebot.types import Message
from b3auth import check_card_b3  # make sure b3auth.py and b3.py are in same folder

@bot.message_handler(commands=['b3'])
def b3_handler(message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        return bot.reply_to(message, "❌ Use format:\n<b>/b3 4111111111111111|12|2026|123</b>", parse_mode="HTML")

    cc_input = args[1].strip()
    bot.send_chat_action(chat_id, "typing")
    result = check_card_b3(cc_input)
    bot.send_message(chat_id, result)
