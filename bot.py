import telebot
import feedparser
import os

# Configurações com variáveis de ambiente
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RSS_FEED_URL = os.environ.get("URL")  # URL do feed RSS
DESTINATION = os.environ.get("DESTINATION", "").split(",")  # Chats de destino

bot = telebot.TeleBot(BOT_TOKEN)

# Comando /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Olá! Envie uma palavra-chave para buscar posts no site."
    )

# Pesquisa por palavra-chave no RSS
@bot.message_handler(func=lambda message: True)
def search_rss(message):
    query = message.text.strip().lower()
    feed = feedparser.parse(RSS_FEED_URL)

    if "entries" not in feed or not feed.entries:
        bot.send_message(message.chat.id, "Erro ao acessar o feed RSS. Tente novamente mais tarde.")
        return

    # Filtra posts com base na palavra-chave
    results = []
    for entry in feed.entries:
        if query in entry.title.lower() or query in entry.summary.lower():
            results.append(f"📌 {entry.title}\n🔗 {entry.link}")

    # Responde ao usuário
    if results:
        reply = "\n\n".join(results[:10])  # Limita a 10 resultados
    else:
        reply = "Não encontrei nenhum post relacionado à sua pesquisa."

    bot.send_message(message.chat.id, reply)

# Inicializa o bot
if __name__ == "__main__":
    bot.polling()
