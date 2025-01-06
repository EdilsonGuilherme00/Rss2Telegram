import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função para buscar posts do site via API
def fetch_posts_from_site(search_term):
    API_URL = os.getenv("API_URL")  # Lê a URL da API dos Secrets
    if not API_URL:
        raise ValueError("API_URL não foi definido nas variáveis de ambiente.")
    
    print(f"Buscando posts com o termo: {search_term}")  # Log do termo de pesquisa
    
    try:
        response = requests.get(API_URL, params={"search": search_term})
        
        # Log de status da resposta da API
        print(f"Status da resposta da API: {response.status_code}")
        
        if response.status_code == 200:
            posts = response.json()
            print(f"Resultados encontrados: {len(posts)} posts.")  # Log do número de posts
            
            # Formata os resultados da API
            return [
                {"id": post["id"], "title": post["title"]["rendered"], "url": post["link"]}
                for post in posts
            ]
        else:
            print(f"Erro ao buscar posts: {response.status_code}")
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
        if len(results) == 1:
            # Se apenas 1 post, exibir o título seguido de um botão para acessar o post
            post = results[0]
            keyboard = [
                [InlineKeyboardButton(post['title'], url=post['url'])]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            response = f"{post['title']} - Clique no botão abaixo para acessar o post."
            await update.message.reply_text(response, reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            # Se mais de 1 post, mostrar a palavra "Baixar" como link
            response = "Resultados encontrados:\n\n"
            for post in results:
                response += f"{post['title']} - [Baixar]({post['url']})\n"
            await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        response = "Nenhum post encontrado para o termo pesquisado."
        await update.message.reply_text(response, disable_web_page_preview=True)

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
