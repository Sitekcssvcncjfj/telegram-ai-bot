from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"

async def cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "/start":
        await update.message.reply_text("Merhaba 🤖 Ben AI botum!")

    elif "merhaba" in text.lower():
        await update.message.reply_text("Merhaba 👋")

    else:
        await update.message.reply_text("Mesajını aldım.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, cevap))

app.run_polling()