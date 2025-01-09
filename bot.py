from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler
import logging
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Obter o token do bot a partir do arquivo .env ou variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado. Certifique-se de que está definido no arquivo .env ou nas variáveis de ambiente.")

# Função de tratamento de consultas em linha
async def inline_query(update, context):
    query = update.inline_query.query  # Obter a consulta do usuário
    results = []

    if query:
        # Criação do resultado para a consulta em linha
        results.append(
            InlineQueryResultArticle(
                id="1",  # ID único para o resultado
                title="Example Title",  # Título do artigo
                input_message_content=InputTextMessageContent(f"Você procurou por: {query}")  # Conteúdo da mensagem que será enviada
            )
        )

    # Responde a consulta com os resultados
    await update.inline_query.answer(results)

# Função principal que inicializa o bot
def main():
    # Inicializa a aplicação com o token do bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Registra o manipulador para consultas em linha
    application.add_handler(InlineQueryHandler(inline_query))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()