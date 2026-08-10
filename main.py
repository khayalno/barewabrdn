import telebot
from telebot import types

# تۆکنەکەت لێرە دابنێ
TOKEN = "8671348131:AAH2sDxkO-jsyuZJ0jPfx0Qy3vlC1x8l430"
bot = telebot.TeleBot(TOKEN)

# داتابەیس بۆ پاشەکەوتکردنی پەیامی بەخێرهاتن و ئەندامان
group_data = {}
admin_welcome = {} 

# ١. فەرمانی /start لە چاتی تایبەت
@bot.message_handler(commands=['start'])
def start_private(message):
    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("➕ زیادکردن بۆ گروپ", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
        markup.add(btn)
        bot.reply_to(message, "👋 السَّلَاْمُ عَلَیْکُم\nبەخێربێیت بۆ بۆتی بەڕێوەبردنی گروپ\n\nبۆ دانانی پەیامی بەخێرهاتن، فەرمانی /setwelcome بنووسە.", reply_markup=markup)

# ٢. دانانی پەیامی بەخێرهاتن لە چاتی تایبەت
@bot.message_handler(commands=['setwelcome'])
def set_welcome(message):
    if message.chat.type == 'private':
        msg = bot.reply_to(message, "✍️ پەیامەکەت بنووسە:\n({name} بۆ تاگ، {group} بۆ ناوی گروپ)")
        bot.register_next_step_handler(msg, save_welcome)

def save_welcome(message):
    admin_welcome[message.from_user.id] = message.text
    bot.reply_to(message, "✅ پەیامەکەت پاشەکەوت کرا.")

# ٣. بەخێرهاتن و سڕینەوەی نامەی چوونەژوورەوە
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    chat_id = message.chat.id
    try: bot.delete_message(chat_id, message.message_id)
    except: pass

    if chat_id not in group_data: group_data[chat_id] = {'members': {}}

    for member in message.new_chat_members:
        if member.id == bot.get_me().id: continue
        group_data[chat_id]['members'][member.id] = member.first_name
        
        # دۆزینەوەی پەیامی ئەدمین
        welcome_text = "بەخێر هاتی بۆ گروپ!"
        for admin in bot.get_chat_administrators(chat_id):
            if admin.user.id in admin_welcome:
                welcome_text = admin_welcome[admin.user.id].replace("{name}", f"[{member.first_name}](tg://user?id={member.id})").replace("{group}", message.chat.title)
                break
        
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")

# ٤. قەدەغەکردنی لینک
@bot.message_handler(func=lambda m: True)
def filter_links(message):
    if message.chat.type in ['group', 'supergroup']:
        text = message.text or message.caption or ""
        if "http" in text or "t.me" in text:
            # پشکنینی ئەدمین
            if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'creator']:
                try: bot.delete_message(message.chat.id, message.message_id)
                except: pass

# ٥. تاگی گشتی
@bot.message_handler(commands=['all', 'tagall'])
def tag_all(message):
    chat_id = message.chat.id
    if chat_id in group_data and group_data[chat_id]['members']:
        text = "📢 ئەندامان:\n" + "".join([f"[{name}](tg://user?id={uid}) " for uid, name in group_data[chat_id]['members'].items()])
        bot.send_message(chat_id, text, parse_mode="Markdown")

bot.infinity_polling()
