import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
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
            
            # Formata os resultados da API incluindo os novos campos
            return [
                {
                    "id": post["id"], 
                    "title": post["title"]["rendered"], 
                    "url": post["link"],
                    "imagem_principal": post.get("imagem_principal", ""),  # Usando campo personalizado imagem_principal
                    "jogo_tem_mod": post.get("jogo_tem_mod", "Não"),
                    "nome_jogo": post.get("nome_jogo", "Desconhecido"),
                    "versao": post.get("versao", "Desconhecida")
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
        # Se o nome_jogo estiver vazio, usamos o título do post
        title = post["nome_jogo"] if post["nome_jogo"] else post["title"]
        versao = post["versao"] if post["versao"] else "Versão Desconhecida"

        # A descrição no modo inline será apenas a versão, se disponível
        description = f"Versão: {versao}"

        # A mensagem enviada quando o usuário clicar no post irá mostrar mais detalhes
        message = (
            f"<b>{title}</b> - Versão: {versao}\n"
            f"Mod: {post.get('jogo_tem_mod', 'Desconhecido')}\n\n"
        )

        # Se houver imagem_principal, envia a imagem com a mensagem
        if post.get('imagem_principal'):
            # Usando InlineQueryResultPhoto para enviar a imagem
            inline_results.append(
                InlineQueryResultPhoto(
                    id=post["id"],
                    title=title,  # Usando o nome_jogo ou o título do post
                    input_message_content=InputTextMessageContent(
                        message,
                        parse_mode="HTML",  # Usando HTML para formatação de texto
                    ),
                    photo_url=post['imagem_principal'],  # URL da imagem que será enviada
                    thumb_url=post['imagem_principal'],  # Miniatura da imagem
                    caption=message  # A mensagem como a legenda da imagem
                )
            )
        else:
            # Se não houver imagem, apenas enviar o título e a versão
            inline_results.append(
                InlineQueryResultArticle(
                    id=post["id"],
                    title=title,
                    input_message_content=InputTextMessageContent(
                        message,
                        parse_mode="HTML",
                    ),
                    description=description,
                )
            )

    # Envia os resultados
    await update.inline_query.answer(inline_results, cache_time=1)

# Função para o comando /start (ainda existe, mas não será utilizado diretamente)
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
