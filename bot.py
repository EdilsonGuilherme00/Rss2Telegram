import telebot
import feedparser

# Configurações
BOT_TOKEN = "SEU_TOKEN_DO_BOT"
RSS_FEED_URL = "https://seusite.com/rss"  # Substitua pelo URL do feed RSS do site
bot = telebot.TeleBot(BOT_TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
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

    # Verifica se o feed é válido
    if 'entries' not in feed or not feed.entries:
        bot.send_message(message.chat.id, "Erro ao acessar o feed RSS. Tente novamente mais tarde.")
        return

    # Filtra posts com base na palavra-chave
    results = []
    for entry in feed.entries:
        if query in entry.title.lower() or query in entry.summary.lower():
            results.append(f"📌 {entry.title}\n🔗 {entry.link}")

    # Responde ao usuário
    if results:
        reply = "\n\n".join(results[:10])  # Limita a 10 resultados para evitar mensagens longas
    else:
        reply = "Não encontrei nenhum post relacionado à sua pesquisa."

    bot.send_message(message.chat.id, reply)

# Inicializar o bot
if __name__ == "__main__":
    bot.polling()
