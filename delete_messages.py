import sqlite3
import os

# Obtendo variáveis de ambiente
TOPIC = os.getenv('TOPIC')
if TOPIC is None:
    print("TOPIC não está definido no ambiente.")
else:
    print(f"TOPIC: {TOPIC}")

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

# Função para deletar todas as mensagens de um tópico específico
def delete_all_messages_from_topic(topic_id):
    print(f"Deletando todas as mensagens do tópico {topic_id}...")
    cursor.execute('DELETE FROM messages WHERE topic_id = ?', (topic_id,))
    conn.commit()

# Exemplo de como usar
create_table()

# Adiciona uma mensagem ao banco de dados no tópico especificado
add_message(TOPIC, 'Esta é uma mensagem de teste.')

# Apaga todas as mensagens do tópico especificado
delete_all_messages_from_topic(TOPIC)

# Fechar a conexão ao banco de dados
conn.close()
