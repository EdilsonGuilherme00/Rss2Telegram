from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá...")

# Configuração do bot
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # O token será armazenado como variável de ambiente
    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona o handler para o comando /start
    application.add_handler(CommandHandler("start", start))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()
