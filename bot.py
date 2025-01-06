import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função para buscar posts no site via Web Scraping
def scrape_posts_from_site(search_term):
    SITE_URL = os.getenv("SITE_URL")  # Lê o URL base do site dos Secrets
    if not SITE_URL:
        raise ValueError("SITE_URL não foi definido nas variáveis de ambiente.")

    try:
        # URL de busca (ajuste conforme necessário)
        response = requests.get(f"{SITE_URL}/busca", params={"q": search_term})
        
        if response.status_code != 200:
            print(f"Erro ao acessar o site: {response.status_code}")
            return []

        # Analisa o HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Ajuste os seletores conforme a estrutura do site
        posts = []
        for post in soup.select(".post"):  # Substitua ".post" pelo seletor correto
            title = post.select_one(".post-title").text.strip()  # Substitua ".post-title" pelo seletor do título
            link = post.select_one("a")["href"]  # Substitua "a" pelo seletor do link
            posts.append({"title": title, "url": link})
        
        return posts
    except Exception as e:
        print(f"Erro durante o scraping: {e}")
        return []

# Função para o comando /pesquisa
async def pesquisa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Verifica se o termo de busca foi fornecido
    if not context.args:
        await update.message.reply_text("Por favor, insira o termo de pesquisa. Exemplo: /pesquisa Python")
        return

    # Termo de busca
    search_term = " ".join(context.args).lower()

    # Busca posts no site usando Web Scraping
    results = scrape_posts_from_site(search_term)

    # Se houver apenas 1 resultado, cria um botão com o link
    if len(results) == 1:
        post = results[0]
        keyboard = [[InlineKeyboardButton("Acessar", url=post['url'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        response = f"Resultado encontrado:\n\n{post['title']}"
        await update.message.reply_text(response, reply_markup=reply_markup)

    # Se houver mais de 1 resultado, cria um botão com a palavra "Baixar"
    elif len(results) > 1:
        response = "Resultados encontrados:\n\n"
        keyboard = []
        for post in results:
            keyboard.append([InlineKeyboardButton("Baixar", url=post['url'])])
            response += f"- {post['title']}\n"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)

    # Se não houver resultados
    else:
        await update.message.reply_text("Nenhum post encontrado para o termo pesquisado.")

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Use /pesquisa <termo> para buscar posts.")

# Configuração do bot
def main():
    TOKEN = os.getenv("BOT_TOKEN")  # Lê o token da variável de ambiente
    if not TOKEN:
        raise ValueError("BOT_TOKEN não foi definido nas variáveis de ambiente.")
    
    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pesquisa", pesquisa))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()
