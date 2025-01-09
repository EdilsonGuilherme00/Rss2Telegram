import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
from tempfile import NamedTemporaryFile

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

        # A mensagem enviada quando o usuário clicar no post irá mostrar mais detalhes
        message = (
            f"<b>Nome do Jogo:</b> {title}\n"
            f"<b>Versão do Jogo:</b> {versao}\n"
            f"<b>Mod:</b> {post.get('jogo_tem_mod', 'Desconhecido')}\n\n"
            "🔴 <i>Por favor, delete esta mensagem se não precisar mais dela.</i>"
        )

        # Adiciona o botão de link para o post
        keyboard = [
            [InlineKeyboardButton("Clique aqui para acessar o post", url=post['url'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Cria o resultado inline
        inline_results.append(
            InlineQueryResultArticle(
                id=post["id"],
                title=title,  # Usando o nome_jogo ou o título do post
                input_message_content=InputTextMessageContent(
                    message,
                    parse_mode="HTML",  # Usando HTML para formatação de texto
                ),
                description=f"Versão: {versao}",  # Descrição com a versão
                thumb_url=post.get("imagem_principal", ""),  # Mostra a miniatura da imagem no inline
                reply_markup=reply_markup  # Inclui o botão de link
            )
        )

    # Envia os resultados
    await update.inline_query.answer(inline_results, cache_time=1)

# Função para enviar o post com a imagem após seleção
async def send_selected_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query_data = update.chosen_inline_result.result_id  # ID do post escolhido pelo usuário
    search_results = fetch_posts_from_site(query_data)

    # Filtra para encontrar o post correto
    post = next((item for item in search_results if item["id"] == query_data), None)

    if post:
        # Formata a mensagem
        title = post["nome_jogo"] if post["nome_jogo"] else post["title"]
        versao = post["versao"] if post["versao"] else "Versão Desconhecida"
        message = (
            f"<b>Nome do Jogo:</b> {title}\n"
            f"<b>Versão do Jogo:</b> {versao}\n"
            f"<b>Mod:</b> {post.get('jogo_tem_mod', 'Desconhecido')}\n\n"
            "🔴 <i>Por favor, delete esta mensagem se não precisar mais dela.</i>"
        )

        # Baixa e envia a imagem temporária
        if post.get('imagem_principal'):
            image_url = post['imagem_principal']
            try:
                with requests.get(image_url, stream=True) as response:
                    response.raise_for_status()
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(response.content)
                        tmp_file_path = tmp_file.name

                # Envia a mensagem com a imagem
                await context.bot.send_photo(
                    chat_id=update.effective_user.id,
                    photo=open(tmp_file_path, 'rb'),
                    caption=message,
                    parse_mode="HTML"
                )

                # Remove o arquivo temporário após envio
                os.remove(tmp_file_path)
            except Exception as e:
                print(f"Erro ao enviar imagem: {e}")

# Configuração do bot
def main():
    TOKEN = os.getenv("BOT_TOKEN")  # Lê o token da variável de ambiente
    if not TOKEN:
        raise ValueError("BOT_TOKEN não foi definido nas variáveis de ambiente.")

    application = ApplicationBuilder().token(TOKEN).build()

    # Adiciona o handler para o modo inline e a escolha do resultado
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(InlineQueryHandler(send_selected_post, block=False))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()