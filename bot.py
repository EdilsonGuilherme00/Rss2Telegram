import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

# Função para buscar posts do site via API
def fetch_posts_from_site(search_term):
    API_URL = os.getenv("API_URL")
    if not API_URL:
        raise ValueError("API_URL não foi definido nas variáveis de ambiente.")
    
    try:
        response = requests.get(API_URL, params={"search": search_term})
        
        if response.status_code == 200:
            posts = response.json()
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
            return []
    except requests.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return []

# Função para baixar a imagem (se existir)
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open("temp_image.jpg", "wb") as f:
                f.write(response.content)
            return "temp_image.jpg"
    except requests.RequestException as e:
        print(f"Erro ao baixar imagem: {e}")
    return None

# Função para consultas inline
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.lower()

    if not query:
        return

    results = fetch_posts_from_site(query)

    if not results:
        return

    inline_results = []
    for post in results:
        title = post["nome_jogo"] if post["nome_jogo"] else post["title"]
        versao = post["versao"] if post["versao"] else "Versão Desconhecida"
        description = f"Versão: {versao}"

        message = f"<b>{title}</b> - Versão: {versao}\nMod: {post.get('jogo_tem_mod', 'Desconhecido')}\n\n"

        keyboard = [
            [InlineKeyboardButton("Clique aqui para acessar o post", url=post['url'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        inline_results.append(
            InlineQueryResultArticle(
                id=post["id"],
                title=title,
                input_message_content=InputTextMessageContent(
                    message,
                    parse_mode="HTML",
                ),
                description=description,
                reply_markup=reply_markup
            )
        )

        if post.get('imagem_principal'):
            # Baixa e envia a imagem, se existir
            image_path = download_image(post['imagem_principal'])
            if image_path:
                inline_results.append(
                    InlineQueryResultArticle(
                        id=f"{post['id']}_image",  
                        title=f"Imagem de {title}",
                        input_message_content=InputMediaPhoto(
                            media=open(image_path, "rb"),
                            caption=message,
                            parse_mode="HTML"
                        ),
                        description=description,
                        reply_markup=reply_markup
                    )
                )

    if not inline_results:
        return

    await update.inline_query.answer(inline_results, cache_time=1)

# Função principal para iniciar o bot
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN não foi definido nas variáveis de ambiente.")
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(InlineQueryHandler(inline_query))
    application.run_polling()

if __name__ == "__main__":
    main()