import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto
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

    # Verifique se há resultados
    if not results:
        print("Nenhum resultado encontrado.")
        return

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

        # Adiciona o botão de link para o post
        keyboard = [
            [InlineKeyboardButton("Clique aqui para acessar o post", url=post['url'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Verificar se a mensagem está configurada corretamente antes de enviar
        print(f"Mensagem para o post {post['id']}: {message}")
        
        # Cria o conteúdo do post
        inline_results.append(
            InlineQueryResultArticle(
                id=post["id"],
                title=title,
                input_message_content=InputTextMessageContent(
                    message,
                    parse_mode="HTML",  # Usando HTML para formatação de texto
                ),
                description=description,  # Descrição com a versão
                reply_markup=reply_markup  # Inclui o botão de link
            )
        )

        # Verifica se existe a imagem principal
        if post.get('imagem_principal'):
            # Adiciona a imagem se o campo estiver presente
            inline_results.append(
                InlineQueryResultArticle(
                    id=f"{post['id']}_image",  # Um id único para a imagem
                    title=f"Imagem de {title}",
                    input_message_content=InputMediaPhoto(
                        media=post['imagem_principal'],
                        caption=message,
                        parse_mode="HTML"
                    ),
                    description=description,
                    reply_markup=reply_markup  # Inclui o botão de link
                )
            )

    # Verifica se existem resultados para retornar
    if not inline_results:
        print("Nenhum resultado de consulta inline foi gerado.")
        return

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
