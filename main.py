import os
import asyncio

from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn
from asgiref.wsgi import WsgiToAsgi

# Load variables from .env
load_dotenv()

# Get Telegram bot token from .env
TOKEN = os.environ["8932718398:AAEbOiSIa_yZGA1LGWBxxT0zlL7TeIDeQ-0"]

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 SMG AI Agent aktif!")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PONG 🟢")


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ping", ping))


flask_app = Flask(__name__)


@flask_app.get("/")
def home():
    return "SMG AI Agent is running."


@flask_app.post("/telegram")
async def telegram_webhook():
    data = request.get_json(force=True)

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return "OK"


async def main():
    await telegram_app.initialize()
    await telegram_app.start()

    port = int(os.environ.get("PORT", 10000))

    external_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not external_url:
        raise RuntimeError(
            "RENDER_EXTERNAL_URL belum tersedia."
        )

    await telegram_app.bot.set_webhook(
        url=f"{external_url}/telegram"
    )

    config = uvicorn.Config(
        WsgiToAsgi(flask_app),
        host="0.0.0.0",
        port=port
    )

    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
