from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os


from telegram_bot import start, add_symptom, add_factor, add_lab, diagnose, data
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Добавляем обработчики команд
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("symptom", add_symptom))
telegram_app.add_handler(CommandHandler("factor", add_factor))
telegram_app.add_handler(CommandHandler("lab", add_lab))
telegram_app.add_handler(CommandHandler("diagnose", diagnose))
telegram_app.add_handler(CommandHandler("clear", clear_data))

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)  # Синхронно получаем данные
    telegram_app.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "DiagLNG бот работает!"

def set_webhook():
    url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook/{BOT_TOKEN}"
    telegram_app.bot.set_webhook(url)

# Запускаем установку webhook при старте
@app.before_first_request
def before_first_request():
    set_webhook()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ["PORT"]))
