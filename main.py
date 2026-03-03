from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import random
import asyncio

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"
openai.api_key = "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"

warnings = {}
bad_words = ["salak","aptal","küfür"]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Merhaba! Ben gelişmiş grup ve AI botuyum!")

# AI
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    soru = " ".join(context.args)

    if not soru:
        await update.message.reply_text("Kullanım: /ai soru")
        return

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":soru}]
    )

    cevap = response.choices[0].message.content
    await update.message.reply_text(cevap)

# MEME
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memes = [
        "😂 Yazılımcı kahve içmeden kod yazamaz",
        "🐛 Bug yok feature var",
        "💻 Kod çalışıyorsa dokunma"
    ]
    await update.message.reply_text(random.choice(memes))

# ZAR
async def zar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sayı = random.randint(1,6)
    await update.message.reply_text(f"🎲 Zar sonucu: {sayı}")

# COIN
async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sonuç = random.choice(["Yazı","Tura"])
    await update.message.reply_text(f"🪙 {sonuç}")

# WARN
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user.id
        warnings[user] = warnings.get(user, 0) + 1
        await update.message.reply_text(f"⚠️ Warn verildi! Toplam warn: {warnings[user]}")

# BAN
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.message.chat.id, user_id)
        await update.message.reply_text("🚫 Kullanıcı banlandı")

# MUTE
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.restrict_chat_member(
            update.message.chat.id,
            user_id,
            permissions={}
        )
        await update.message.reply_text("🔇 Kullanıcı susturuldu")

# HOŞGELDİN
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Hoş geldin {user.first_name}")

# KÜFÜR FİLTRESİ
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    for word in bad_words:
        if word in text:
            await update.message.delete()
            await update.message.reply_text("⚠️ Küfür yasak!")
            break

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("zar", zar))
app.add_handler(CommandHandler("coin", coin))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("mute", mute))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_bad_words))

print("Bot çalışıyor...")
app.run_polling()
