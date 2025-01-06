import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função para buscar posts do site via API
def fetch_posts_from_site(search_term):
    API_URL = os.getenv("API_URL")  # Lê a URL da API dos Secrets
    if not API_URL:
        raise ValueError("API_URL não foi definido nas variáveis de ambiente.")

    try:
        response = requests.get(API_URL, params={"search": search_term})
        if response.status_code == 200:
            posts = response.json()
            # Formata os resultados da API
            return [
                {"id": post["id"], "title": post["title"]["rendered"], "url": post["link"]}
                for post in posts
            ]
        else:
            return []
    except requests.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return []

# Função para o comando /pesquisa
async def pesquisa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Verifica se o termo de busca foi fornecido
    if not context.args:
        await update.message.reply_text("Por favor, insira o termo de pesquisa. Exemplo: /pesquisa Python")
        return

    # Termo de busca
    search_term = " ".join(context.args).lower()

    # Busca posts no site usando a API
    results = fetch_posts_from_site(search_term)

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
