from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import openai

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"
openai.api_key = os.getenv(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
)

warnings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Ben gelişmiş AI botuyum 🤖")

# AI komutu
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

# Meme komutu
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😂 Bugünün memesi: Yazılımcı kahve içmeden kod yazamaz!")

# Warn sistemi
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user.id
        warnings[user] = warnings.get(user, 0) + 1
        await update.message.reply_text(f"⚠️ Kullanıcı uyarıldı! Toplam warn: {warnings[user]}")

# Ban sistemi
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.message.chat.id, user_id)
        await update.message.reply_text("🚫 Kullanıcı banlandı.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))

app.run_polling()
