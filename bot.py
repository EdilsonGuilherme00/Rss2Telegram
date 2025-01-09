from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler
import logging

# Configuração do log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # Substitua 'YOUR_TOKEN' pelo seu token do bot do Telegram
    application = Application.builder().token("YOUR_TOKEN").build()

    # Registra o manipulador para consultas em linha
    application.add_handler(InlineQueryHandler(inline_query))

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()