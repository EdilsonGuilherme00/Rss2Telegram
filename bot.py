import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função para buscar posts no site via Web Scraping
def scrape_posts_from_site(search_term):
    SITE_URL = os.getenv("SITE_URL")  # Lê o URL base do site dos Secrets
    if not SITE_URL:
        raise ValueError("SITE_URL não foi definido nas variáveis de ambiente.")

    try:
        # URL de busca com o parâmetro ?s=
        search_url = f"{SITE_URL}/?s={search_term}"

        response = requests.get(search_url)
        
        if response.status_code != 200:
            print(f"Erro ao acessar o site: {response.status_code}")
            return []

        # Analisa o HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Ajuste os seletores conforme a estrutura do site
        posts = []
        for post in soup.find_all("article"):  # Artigos são geralmente representados por <article>
            title_tag = post.find("h2")  # O título do post geralmente está dentro de <h2>
            if title_tag:
                title = title_tag.text.strip()
                link = post.find("a")["href"]  # Link do post
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

    # Responde com os resultados ou mensagem de não encontrado
    if results:
        response = "Resultados encontrados:\n\n"
        for post in results:
            response += f"- [{post['title']}]({post['url']})\n"
    else:
        response = "Nenhum post encontrado para o termo pesquisado."

    # Envia a resposta
    await update.message.reply_text(response, parse_mode="Markdown")

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
