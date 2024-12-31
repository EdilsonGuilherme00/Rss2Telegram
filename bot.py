import telebot
import feedparser

# Configurações
BOT_TOKEN = "8130718516:AAF0Zsl-p9zqd9uYfRhOPHWcgP6BjzSdCaE"
RSS_FEED_URL = "https://zonaproibida.com/category/todos/feed/"  # Substitua pelo URL do feed RSS do site
bot = telebot.TeleBot(BOT_TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
def start(message):
    print("Comando /start recebido")
    bot.send_message(
        message.chat.id,
        "Oi! Estou aqui para ajudar, o que deseja?"
    )

# Comando /pesquisa para buscar posts
@bot.message_handler(commands=['pesquisa'])
def search_rss(message):
    print(f"Comando /pesquisa recebido: {message.text}")
    query = message.text.strip().replace('/pesquisa', '').strip().lower()

    # Verifica se a pesquisa está vazia
    if not query:
        bot.send_message(message.chat.id, "Por favor, forneça um título ou palavra-chave para a pesquisa.")
        return

    # Obtém o feed RSS
    print("Buscando no RSS Feed...")
    feed = feedparser.parse(RSS_FEED_URL)

    # Verifica se o feed é válido
    if 'entries' not in feed or not feed.entries:
        bot.send_message(message.chat.id, "Erro ao acessar o feed RSS. Tente novamente mais tarde.")
        return

    # Filtra os posts com base na palavra-chave
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
    print("Bot iniciado")
    bot.polling()
