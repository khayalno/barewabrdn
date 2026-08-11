import telebot
from telebot import types

# تۆکنەکەت لێرە دابنێ
TOKEN = "8671348131:AAF-BKG3-BniXncrNaKr2H8LzA2abiB4psk"
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

# ٢. دانانی پەیامی بەخێرهاتن
@bot.message_handler(commands=['setwelcome'])
def set_welcome(message):
    if message.chat.type == 'private':
        msg = bot.reply_to(message, "✍️ پەیامی بەخێرهاتن بنوسە:\n(بۆ ناوی گروپ {group}، بۆ تاگ {name})")
        bot.register_next_step_handler(msg, save_welcome)

def save_welcome(message):
    admin_welcome[message.chat.id] = message.text
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
        
        # دیاریکردنی پەیامی بەخێرهاتن
        welcome_text = "بەخێر هاتیت بۆ گرووپەکەمان {name}"
        if chat_id in admin_welcome:
            welcome_text = admin_welcome[chat_id]
            
        welcome_text = welcome_text.replace("{name}", f"[{member.first_name}](tg://user?id={member.id})").replace("{group}", message.chat.title)
        
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")

# ٤. قەدەغەکردنی لینک
@bot.message_handler(func=lambda m: True, content_types=['text', 'caption'])
def filter_links(message):
    if message.chat.type in ['group', 'supergroup']:
        text = message.text or message.caption or ""
        if "http" in text or "t.me" in text:
            try:
                member_status = bot.get_chat_member(message.chat.id, message.from_user.id).status
                if member_status not in ['administrator', 'creator']:
                    bot.delete_message(message.chat.id, message.message_id)
            except:
                pass

# ٥. تاگی گشتی (تەنها بۆ ئەدمین)
@bot.message_handler(commands=['all', 'tagall'])
def tag_all(message):
    chat_id = message.chat.id
    if message.chat.type in ['group', 'supergroup']:
        try:
            member_status = bot.get_chat_member(chat_id, message.from_user.id).status
            if member_status in ['administrator', 'creator']:
                if chat_id in group_data and group_data[chat_id]['members']:
                    text = "📢 ئەندامان:\n" + "".join([f"[{name}](tg://user?id={uid}) " for uid, name in group_data[chat_id]['members'].items()])
                    bot.send_message(chat_id, text, parse_mode="Markdown")
                else:
                    bot.reply_to(message, "⚠️ هیچ ئەندامێک تۆمار نەکراوە لە داتابەیسدا.")
            else:
                bot.reply_to(message, "❌ ببورە، ئەم فەرمانە تەنها بۆ ئەدمینەکانە!")
        except Exception as e:
            bot.reply_to(message, "⚠️ هەڵەیەک ڕوودا.")

bot.infinity_polling()
