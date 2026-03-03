import logging
import time
import re
import random
import platform

from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from groq import Groq

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"
GROQ_API = "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"

client = Groq(api_key=GROQ_API)

logging.basicConfig(level=logging.INFO)

memory = {}
warnings = {}
muted_users = set()

bad_words = [
    "amk","aq","orospu","piç","siktir","ananı","salak"
]

rules_text = "Henüz kural ayarlanmadı."
start_time = time.time()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🤖 AI", callback_data="menu_ai")],
        [InlineKeyboardButton("🖼 Resim", callback_data="menu_img")],
        [InlineKeyboardButton("⚡ Komutlar", callback_data="menu_commands")]
    ]

    await update.message.reply_text(
        "🤖 DEV AI BOT\n\nMenüyü kullan.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "menu_ai":

        await query.edit_message_text(
            "🤖 AI sohbet\n\n/ai mesaj"
        )

    elif query.data == "menu_img":

        await query.edit_message_text(
            "🖼 Resim oluştur\n\n/img açıklama"
        )

    elif query.data == "menu_commands":

        await query.edit_message_text(
            "/ai\n/img\n/joke\n/meme\n/coin\n/roll\n/8ball"
        )


async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    mesaj = " ".join(context.args)

    if not mesaj:
        await update.message.reply_text("Kullanım: /ai mesaj")
        return

    if user not in memory:

        memory[user] = [
            {"role":"system","content":"Türkçe konuşan Telegram AI botsun."}
        ]

    memory[user].append({"role":"user","content":mesaj})

    response = client.chat.completions.create(
        messages=memory[user],
        model="llama-3.1-8b-instant"
    )

    cevap = response.choices[0].message.content

    memory[user].append({"role":"assistant","content":cevap})

    await update.message.reply_text(cevap)


async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):

    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("/img açıklama")
        return

    await update.message.reply_text(
        f"🖼 Resim oluşturuluyor:\n{prompt}"
    )


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):

    jokes = [
        "Programcı duş almaz çünkü bug vardır",
        "Yazılımcı kahve içer çünkü Java"
    ]

    await update.message.reply_text(random.choice(jokes))


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):

    memes = [
        "https://i.imgflip.com/1bij.jpg",
        "https://i.imgflip.com/26am.jpg"
    ]

    await update.message.reply_photo(random.choice(memes))


async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(random.choice(["Yazı","Tura"]))


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(str(random.randint(1,6)))


async def ball(update: Update, context: ContextTypes.DEFAULT_TYPE):

    answers = ["Evet","Hayır","Belki","Kesinlikle"]

    await update.message.reply_text(random.choice(answers))


async def avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photos = await context.bot.get_user_profile_photos(update.message.from_user.id)

    if photos.total_count > 0:
        await update.message.reply_photo(photos.photos[0][0].file_id)


async def userid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(str(update.message.from_user.id))


async def mention(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    await update.message.reply_text(
        f"[{user.first_name}](tg://user?id={user.id})",
        parse_mode="Markdown"
    )
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Mesaja cevap ver.")
        return

    user = update.message.reply_to_message.from_user.id

    if user not in warnings:
        warnings[user] = 0

    warnings[user] += 1

    await update.message.reply_text(
        f"⚠ Warn verildi\nToplam: {warnings[user]}"
    )

    if warnings[user] >= 3:

        await context.bot.ban_chat_member(
            update.effective_chat.id,
            user
        )

        await update.message.reply_text("🚫 Kullanıcı banlandı")


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    await context.bot.ban_chat_member(
        update.effective_chat.id,
        user
    )

    await update.message.reply_text("🚫 Banlandı")


async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    await context.bot.ban_chat_member(update.effective_chat.id,user)
    await context.bot.unban_chat_member(update.effective_chat.id,user)

    await update.message.reply_text("👢 Kicklendi")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    permissions = ChatPermissions(can_send_messages=False)

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        permissions
    )

    await update.message.reply_text("🔇 Mute edildi")


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        permissions
    )

    await update.message.reply_text("🔊 Unmute edildi")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("/clear sayı")
        return

    count = int(context.args[0])

    for i in range(count):

        try:

            await context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id - i
            )

        except:
            pass


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(rules_text)


async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global rules_text

    rules_text = " ".join(context.args)

    await update.message.reply_text("Kurallar güncellendi")


async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if re.search(r"http|https|t.me", text):

        await update.message.delete()

        await update.message.reply_text("🚫 Link yasak")


async def badword_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    for word in bad_words:

        if word in text:

            await update.message.delete()

            await update.message.reply_text("🚫 Küfür yasak")

            break


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for user in update.message.new_chat_members:

        await update.message.reply_text(
            f"👋 Hoşgeldin {user.first_name}"
        )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🏓 Pong")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uptime = int(time.time() - start_time)

    await update.message.reply_text(f"Uptime: {uptime}")


async def botinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("DEV AI BOT")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("img", img))

app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("coin", coin))
app.add_handler(CommandHandler("roll", roll))
app.add_handler(CommandHandler("8ball", ball))

app.add_handler(CommandHandler("avatar", avatar))
app.add_handler(CommandHandler("userid", userid))
app.add_handler(CommandHandler("mention", mention))

app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("clear", clear))

app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("setrules", setrules))

app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("botinfo", botinfo))

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_links))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), badword_filter))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

app.add_handler(CallbackQueryHandler(menu_buttons))

print("BOT ÇALIŞIYOR 🚀")

app.run_polling()
