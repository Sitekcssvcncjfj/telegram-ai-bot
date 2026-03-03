import logging
import time
import re
import random
import platform
from telegram import Update, ChatPermissions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TOKEN = "8787679143:AAGRBpARDCSG5-ktbmf_fLiIFaDT7IuwP2s"
GROQ_API = "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"

client = Groq(api_key=GROQ_API)

logging.basicConfig(level=logging.INFO)

memory = {}
warnings = {}
bad_words = [
    "amk",
    "aq",
    "orospu",
    "piç",
    "siktir",
    "ananı",
    "salak"
]

async def badword_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.text:
        return

    text = update.message.text.lower()

    for word in bad_words:

        if word in text:

            await update.message.delete()

            await update.message.reply_text("🚫 Küfür yasak")

            break

rules_text = "Henüz kural ayarlanmadı."
start_time = time.time()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 DEV AI BOT\n\n"
        "/ai mesaj\n"
        "/img prompt\n"
        "/dev\n"
    )

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    mesaj = " ".join(context.args)

    if not mesaj:
        await update.message.reply_text("Kullanım:\n/ai mesaj")
        return

    if user not in memory:
        memory[user] = []

        memory[user].append({
            "role": "system",
            "content": "Sen bir Telegram AI botsun ve sadece Türkçe cevap verirsin. Her zaman Türkçe konuş."
        })

    memory[user].append({"role": "user", "content": mesaj})

    response = client.chat.completions.create(
        messages=memory[user],
        model="llama-3.1-8b-instant"
    )

    cevap = response.choices[0].message.content
    memory[user].append({"role": "assistant", "content": cevap})

    await update.message.reply_text(cevap)

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):

    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("Kullanım:\n/img açıklama")
        return

    await update.message.reply_text(
        f"🖼 Resim oluşturuluyor:\n{prompt}\n\n"
        "AI image API ekleyince gerçek resim üretecek."
    )

async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⚡ DEV BOT PANEL\n\n"
        "🤖 AI\n"
        "/ai\n/ask\n/translate\n/code\n/fixcode\n/explain\n/story\n/idea\n\n"
        "😂 Eğlence\n"
        "/joke\n/meme\n/coin\n/roll\n/8ball\n\n"
        "👮 Moderasyon\n"
        "/ban\n/kick\n/mute\n/unmute\n/warn\n/clear\n\n"
        "⚙ Sistem\n"
        "/ping\n/stats\n/botinfo\n/uptime"
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai(update, context)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    response = client.chat.completions.create(
        messages=[{"role":"user","content":"translate: "+text}],
        model="llama-3.1-8b-instant"
    )
    await update.message.reply_text(response.choices[0].message.content)

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=" ".join(context.args)
    r=client.chat.completions.create(messages=[{"role":"user","content":"write code: "+text}],model="llama-3.1-8b-instant")
    await update.message.reply_text(r.choices[0].message.content)

async def fixcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=" ".join(context.args)
    r=client.chat.completions.create(messages=[{"role":"user","content":"fix this code: "+text}],model="llama-3.1-8b-instant")
    await update.message.reply_text(r.choices[0].message.content)

async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=" ".join(context.args)
    r=client.chat.completions.create(messages=[{"role":"user","content":"explain: "+text}],model="llama-3.1-8b-instant")
    await update.message.reply_text(r.choices[0].message.content)

async def story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=" ".join(context.args)
    r=client.chat.completions.create(messages=[{"role":"user","content":"write story: "+text}],model="llama-3.1-8b-instant")
    await update.message.reply_text(r.choices[0].message.content)

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r=client.chat.completions.create(messages=[{"role":"user","content":"give startup idea"}],model="llama-3.1-8b-instant")
    await update.message.reply_text(r.choices[0].message.content)

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes=["Programcı duş almaz çünkü bug vardır","Yazılımcı kahve içer çünkü Java"]
    await update.message.reply_text(random.choice(jokes))

async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memes=["https://i.imgflip.com/1bij.jpg","https://i.imgflip.com/26am.jpg"]
    await update.message.reply_photo(random.choice(memes))

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["Yazı","Tura"]))

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(random.randint(1,6)))

async def ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans=["Evet","Hayır","Belki","Kesinlikle"]
    await update.message.reply_text(random.choice(ans))

async def avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos=await context.bot.get_user_profile_photos(update.message.from_user.id)
    if photos.total_count>0:
        await update.message.reply_photo(photos.photos[0][0].file_id)

async def userid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.message.from_user.id))

async def mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user=update.message.from_user
    await update.message.reply_text(f"[{user.first_name}](tg://user?id={user.id})",parse_mode="Markdown")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for user in update.message.new_chat_members:

        await update.message.reply_text(
            f"👋 Hoşgeldin {user.first_name}\nKuralları okumayı unutma."
        )

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count=await context.bot.get_chat_member_count(update.effective_chat.id)
    await update.message.reply_text(f"👥 Üye sayısı: {count}")

async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    a=await context.bot.get_chat_administrators(update.effective_chat.id)
    text="👮 Adminler:\n"
    for i in a:
        text+=i.user.first_name+"\n"
    await update.message.reply_text(text)

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Bir mesaja cevap vererek warn ver.")
        return

    user = update.message.reply_to_message.from_user.id

    if user not in warnings:
        warnings[user] = 0

    warnings[user] += 1

    await update.message.reply_text(
        f"⚠ Uyarı verildi\nToplam warn: {warnings[user]}"
    )

    if warnings[user] >= 3:

        await context.bot.ban_chat_member(
            update.effective_chat.id,
            user
        )

        await update.message.reply_text("🚫 Kullanıcı banlandı.")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(rules_text)

async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global rules_text
    rules_text=" ".join(context.args)
    await update.message.reply_text("Kurallar güncellendi")

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("👮 Adminler", callback_data="admins")],
        [InlineKeyboardButton("📊 Üye Sayısı", callback_data="members")],
        [InlineKeyboardButton("🤖 Bot Bilgi", callback_data="botinfo")]
    ]

    await update.message.reply_text(
        "⚙ Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def panel_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "admins":

        admins = await context.bot.get_chat_administrators(query.message.chat.id)

        text="👮 Adminler\n"

        for a in admins:
            text += a.user.first_name + "\n"

        await query.edit_message_text(text)

    elif query.data == "members":

        count = await context.bot.get_chat_member_count(query.message.chat.id)

        await query.edit_message_text(f"👥 Üye sayısı: {count}")

    elif query.data == "botinfo":

        await query.edit_message_text("🤖 DEV AI BOT")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime=int(time.time()-start_time)
    await update.message.reply_text(f"Uptime: {uptime}")

async def botinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("DEV AI BOT v3")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stats(update,context)

async def server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(platform.system())

async def ai_group(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.text and "@"+context.bot.username in update.message.text:

        soru = update.message.text.replace("@"+context.bot.username,"")

        response = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Sen Türkçe konuşan bir Telegram AI botsun."},
                {"role":"user","content":soru}
            ],
            model="llama-3.1-8b-instant"
        )

        cevap = response.choices[0].message.content

        await update.message.reply_text(cevap)

async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if re.search(r"http|t.me|https", text):

        await update.message.delete()

        await update.message.reply_text("🚫 Link yasak")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("img", img))
app.add_handler(CommandHandler("dev", dev))

app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(CommandHandler("code", code))
app.add_handler(CommandHandler("fixcode", fixcode))
app.add_handler(CommandHandler("explain", explain))
app.add_handler(CommandHandler("story", story))
app.add_handler(CommandHandler("idea", idea))

app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("coin", coin))
app.add_handler(CommandHandler("roll", roll))
app.add_handler(CommandHandler("8ball", ball))

app.add_handler(CommandHandler("avatar", avatar))
app.add_handler(CommandHandler("userid", userid))
app.add_handler(CommandHandler("mention", mention))

app.add_handler(CommandHandler("members", members))
app.add_handler(CommandHandler("admins", admins))

app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("setrules", setrules))

app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("botinfo", botinfo))
app.add_handler(CommandHandler("uptime", uptime))
app.add_handler(CommandHandler("server", server))

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_links))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("panel", panel))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), badword_filter))

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_group))

app.add_handler(CallbackQueryHandler(panel_buttons))

OWNER_ID = 6101127840

ai_users = set()

async def allowai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Bir kullanıcıya cevap ver.")
        return

    user = update.message.reply_to_message.from_user.id
    ai_users.add(user)

    await update.message.reply_text("✅ AI kullanma izni verildi")

async def removeai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Bir kullanıcıya cevap ver.")
        return

    user = update.message.reply_to_message.from_user.id

    if user in ai_users:
        ai_users.remove(user)

    await update.message.reply_text("❌ AI izni kaldırıldı")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Banlamak için mesaja cevap ver")
        return

    user = update.message.reply_to_message.from_user.id

    await context.bot.ban_chat_member(update.effective_chat.id, user)

    await update.message.reply_text("🚫 Kullanıcı banlandı")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("/unban userid")
        return

    user = int(context.args[0])

    await context.bot.unban_chat_member(update.effective_chat.id, user)

    await update.message.reply_text("✅ Ban kaldırıldı")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Kick için cevap ver")
        return

    user = update.message.reply_to_message.from_user.id

    await context.bot.ban_chat_member(update.effective_chat.id, user)
    await context.bot.unban_chat_member(update.effective_chat.id, user)

    await update.message.reply_text("👢 Kullanıcı kicklendi")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Mute için cevap ver")
        return

    user = update.message.reply_to_message.from_user.id

    permissions = ChatPermissions(can_send_messages=False)

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        permissions
    )

    await update.message.reply_text("🔇 Kullanıcı mute edildi")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Unmute için cevap ver")
        return

    user = update.message.reply_to_message.from_user.id

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        permissions
    )

    await update.message.reply_text("🔊 Kullanıcı unmute edildi")

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

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("clear", clear))

app.add_handler(CommandHandler("allowai", allowai))
app.add_handler(CommandHandler("removeai", removeai))

print("BOT ÇALIŞIYOR 🚀")

app.run_polling()