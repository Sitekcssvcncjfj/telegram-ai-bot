import logging
import time
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

from groq import Groq

# =====================
# AYARLAR
# =====================

BOT_TOKEN = "8601721344:AAFAX2X18OIB5EJRtLH6bC5PeqHHk39_lBc"
GROQ_API_KEY = "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"
SD_API_KEY = "e9UllPJBSNKpNceRl1nCPTaHw8TFFXKezYIPXB5oniYiKdXlACheJE32JcGb"

OWNER_ID = 905372292738
SUPPORT_USERNAME = "@garibansikenholding"
BOT_USERNAME = "@AminogluAlBot"

groq_client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

# =====================
# HAFIZA
# =====================

memory = {}

# =====================
# PREMIUM
# =====================

premium_users = set()

# =====================
# LIMIT
# =====================

usage = {}

LIMIT_AI = 10
LIMIT_IMG = 3

DAY = 86400

def check_limit(user, feature):

    if user == OWNER_ID or user in premium_users:
        return True

    now = time.time()

    if user not in usage:
        usage[user] = {"time": now, "ai": 0, "img": 0}

    if now - usage[user]["time"] > DAY:
        usage[user] = {"time": now, "ai": 0, "img": 0}

    if usage[user][feature] >= (LIMIT_AI if feature=="ai" else LIMIT_IMG):
        return False

    usage[user][feature] += 1
    return True

# =====================
# START
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [InlineKeyboardButton(
            "➕ Beni Gruba Ekle",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )],

        [InlineKeyboardButton(
            "🆘 Destek",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )],

        [InlineKeyboardButton(
            "📜 Komutlar",
            callback_data="commands"
        )]

    ]

    await update.message.reply_text(

        "🤖 Ben HayriPotter'in ürettiği yapay zekayım.\n"
        "Size nasıl yardımcı olabilirim?",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )

# =====================
# KOMUT MENU
# =====================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(

        "📜 Komutlar\n\n"
        "/ai mesaj\n"
        "/img açıklama\n"
        "/code kod isteği (premium)\n"
        "/limit\n\n"
        "Grup içinde beni etiketleyerek konuşabilirsiniz."

    )

# =====================
# AI
# =====================

SYSTEM_PROMPT = """
Sen HayriPotter tarafından yapılmış bir Telegram yapay zekasısın.
Sadece Türkçe konuş.
Cevapların kısa ve net olsun.
"""

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    text = " ".join(context.args)

    if not check_limit(user,"ai"):
        await update.message.reply_text("❌ Günlük AI limitin doldu")
        return

    if user not in memory:
        memory[user] = [{"role":"system","content":SYSTEM_PROMPT}]

    memory[user].append({"role":"user","content":text})

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=memory[user]
    )

    reply = response.choices[0].message.content

    memory[user].append({"role":"assistant","content":reply})

    await update.message.reply_text(reply)

# =====================
# CODE (PREMIUM)
# =====================

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in premium_users and user != OWNER_ID:
        await update.message.reply_text(
            "❌ Kod üretme sadece Premium kullanıcılar için."
        )
        return

    prompt = " ".join(context.args)

    messages = [
        {"role":"system","content":"Kod yazan bir AI'sın. Sadece kod üret."},
        {"role":"user","content":prompt}
    ]

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    await update.message.reply_text(response.choices[0].message.content)

# =====================
# AI RESIM
# =====================

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    prompt = " ".join(context.args)

    if not check_limit(user,"img"):
        await update.message.reply_text("❌ Günlük resim limitin doldu")
        return

    await update.message.reply_text("🎨 Resim oluşturuluyor...")

    url = "https://stablediffusionapi.com/api/v3/text2img"

    payload = {
        "key": SD_API_KEY,
        "prompt": prompt,
        "width": "512",
        "height": "512",
        "samples": "1"
    }

    r = requests.post(url,json=payload).json()

    image = r["output"][0]

    await update.message.reply_photo(image)

# =====================
# LIMIT
# =====================

async def limit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user in premium_users or user==OWNER_ID:

        await update.message.reply_text(
            "💎 Premium kullanıcı\nSınırsız kullanım"
        )
        return

    ai = usage.get(user,{}).get("ai",0)
    img = usage.get(user,{}).get("img",0)

    await update.message.reply_text(

        f"📊 Limit\n\n"
        f"AI: {ai}/{LIMIT_AI}\n"
        f"Resim: {img}/{LIMIT_IMG}"

    )

# =====================
# PREMIUM
# =====================

async def addpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != OWNER_ID:
        return

    user = int(context.args[0])
    premium_users.add(user)

    await update.message.reply_text("✅ Premium verildi")

async def delpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != OWNER_ID:
        return

    user = int(context.args[0])
    premium_users.discard(user)

    await update.message.reply_text("❌ Premium kaldırıldı")

# =====================
# ETIKET AI
# =====================

async def mention_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    if f"@{BOT_USERNAME.lower()}" not in text:
        return

    user = update.message.from_user.id
    clean = text.replace(f"@{BOT_USERNAME.lower()}","")

    if not check_limit(user,"ai"):
        return

    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":clean}
    ]

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    await update.message.reply_text(
        response.choices[0].message.content
    )

# =====================
# BOT
# =====================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("ai",ai))
app.add_handler(CommandHandler("img",img))
app.add_handler(CommandHandler("code",code))
app.add_handler(CommandHandler("limit",limit))

app.add_handler(CommandHandler("addpremium",addpremium))
app.add_handler(CommandHandler("delpremium",delpremium))

app.add_handler(CallbackQueryHandler(menu))

app.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), mention_ai)
)

print("BOT ÇALIŞIYOR 🚀")

app.run_polling()
