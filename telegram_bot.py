from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import os

TOKEN = os.environ.get("BOT_TOKEN")
user_data = {}
app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"symptoms": [], "factors": [], "labs": []}
    await update.message.reply_text("Привет! Я бот DiagLNG для диагностики ЛНГ.\n/symptom <текст>\n/factor <текст>\n/lab <текст>\n/diagnose\n/clear")

async def diagnose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_data.get(uid, {"symptoms": [], "factors": [], "labs": []})
    conn = sqlite3.connect("diagnosis.db")
    cursor = conn.cursor()
    matches = set()
    for s in data["symptoms"]:
        for f in data["factors"]:
            for l in data["labs"]:
                s, f, l = s.strip().lower(), f.strip().lower(), l.strip().lower()
                cursor.execute("SELECT diagnosis FROM rules WHERE lower(symptom) LIKE ? AND lower(factor) LIKE ? AND lower(lab) LIKE ?", (f"%{s}%", f"%{f}%", f"%{l}%"))
                for row in cursor.fetchall():
                    matches.add(row[0])
    conn.close()
    msg = "🧠 Возможные диагнозы:\n" + "\n".join(f"• {m}" for m in matches) if matches else "❌ Диагнозы не найдены."
    await update.message.reply_text(msg)

async def add_symptom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    uid = update.effective_user.id
    user_data.setdefault(uid, {"symptoms": [], "factors": [], "labs": []})
    user_data[uid]["symptoms"].append(text)
    await update.message.reply_text(f"✅ Симптом добавлен: {text}")

async def add_factor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    uid = update.effective_user.id
    user_data.setdefault(uid, {"symptoms": [], "factors": [], "labs": []})
    user_data[uid]["factors"].append(text)
    await update.message.reply_text(f"✅ Фактор добавлен: {text}")

async def add_lab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    uid = update.effective_user.id
    user_data.setdefault(uid, {"symptoms": [], "factors": [], "labs": []})
    user_data[uid]["labs"].append(text)
    await update.message.reply_text(f"✅ Анализ добавлен: {text}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"symptoms": [], "factors": [], "labs": []}
    await update.message.reply_text("🗑️ Данные очищены.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("symptom", add_symptom))
telegram_app.add_handler(CommandHandler("factor", add_factor))
telegram_app.add_handler(CommandHandler("lab", add_lab))
telegram_app.add_handler(CommandHandler("diagnose", diagnose))
telegram_app.add_handler(CommandHandler("clear", clear))

@app.post(f"/{TOKEN}")
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

