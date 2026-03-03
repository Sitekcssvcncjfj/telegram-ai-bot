from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import openai

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"
openai.api_key = "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"

bad_words = ["küfür1","küfür2"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Ben gelişmiş AI botuyum 🤖")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    for word in bad_words:
        if word in text:
            await update.message.reply_text("⚠️ Küfür yasak!")
            return

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":text}]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, ai_chat))

app.run_polling()
