import sqlite3
import os
from datetime import datetime, timedelta
import time

# Obtendo variáveis de ambiente
TOPIC = os.getenv('TOPIC')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Função para criar a tabela de mensagens, se não existir
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()

# Função para adicionar uma mensagem ao banco de dados
def add_message(topic_id, message):
    cursor.execute('INSERT INTO messages (topic_id, message) VALUES (?, ?)', (topic_id, message))
    conn.commit()

# Função para apagar mensagens após 24 horas
def delete_old_messages():
    cutoff_time = datetime.now() - timedelta(hours=24)
    cursor.execute('DELETE FROM messages WHERE timestamp < ?', (cutoff_time,))
    conn.commit()

# Função para apagar mensagens de um tópico específico após 24 horas
def delete_messages_from_topic(topic_id):
    cutoff_time = datetime.now() - timedelta(hours=24)
    cursor.execute('DELETE FROM messages WHERE topic_id = ? AND timestamp < ?', (topic_id, cutoff_time))
    conn.commit()

# Exemplo de como usar
create_table()

# Suponha que uma mensagem foi adicionada com um topic_id obtido da variável TOPIC
add_message(TOPIC, 'Esta é uma mensagem de teste.')

# Apaga mensagens de tópico com ID TOPIC após 24 horas
delete_messages_from_topic(TOPIC)

# Fechar a conexão ao banco de dados
conn.close()