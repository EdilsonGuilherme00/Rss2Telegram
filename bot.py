import os
import requests
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

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
                {
                    "id": post["id"],
                    "title": post["title"]["rendered"],
                    "url": post["link"],
                    "versao": post.get("versao", "Desconhecida"),
                    "jogo_tem_mod": post.get("jogo_tem_mod", "Não")
                }
                for post in posts
            ]
        else:
            print(f"Erro ao buscar posts: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return []

# Função para consultas inline
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.lower()

    if not query:
        return

    # Busca posts no site
    results = fetch_posts_from_site(query)

    # Formata os resultados para o modo inline
    inline_results = []
    for post in results:
        # Título do post
        title = post["title"]
        versao = post["versao"] if post["versao"] else "Versão Desconhecida"

        # Descrição no modo inline será apenas a versão, se disponível
        description = f"Versão: {versao}"

        # Mensagem que será mostrada na prévia
        message = (
            f"<b>{title}</b> - Versão: {versao}\n"
            f"Mod: {post.get('jogo_tem_mod', 'Desconhecido')}\n\n"
        )

        # Cria o resultado inline (sem imagem)
        inline_results.append(
            InlineQueryResultArticle(
                id=post["id"],
                title=title,  # Usando o nome do post
                input_message_content=InputTextMessageContent(
                    message,
                    parse_mode="HTML",  # Usando HTML para formatação de texto
                ),
                description=description,  # Descrição com a versão
                url=post["url"]  # Link para o post
            )
        )

    # Envia os resultados inline
    await update.inline_query.answer(inline_results, cache_time=1)

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Use @seubot <termo> no modo inline para buscar posts.")

# Configuração do bot
def main():
    TOKEN = os.getenv("BOT_TOKEN")  # Lê o token da variável de ambiente
    if not TOKEN:
        raise ValueError("BOT_TOKEN não foi definido nas variáveis de ambiente.")

    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona o handler para o modo inline
    application.add_handler(InlineQueryHandler(inline_query))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()