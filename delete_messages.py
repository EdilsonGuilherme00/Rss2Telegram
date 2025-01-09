import sqlite3
import os

# Obtendo variáveis de ambiente
TOPIC = os.getenv('TOPIC')
if TOPIC is None:
    print("TOPIC não está definido no ambiente.")
    TOPIC = "1"  # Valor padrão para fins de teste
else:
    print(f"TOPIC: {TOPIC}")

# Certifique-se de que TOPIC seja tratado como string
try:
    TOPIC = int(TOPIC)
except ValueError:
    print("TOPIC deve ser um número inteiro. Usando valor padrão 1.")
    TOPIC = 1

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Função para criar a tabela de mensagens, se não existir
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        message TEXT NOT NULL,
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
    print(f"Mensagens do tópico {topic_id} foram deletadas.")

# Função para listar todas as mensagens de um tópico
def list_messages_from_topic(topic_id):
    cursor.execute('SELECT id, message, timestamp FROM messages WHERE topic_id = ?', (topic_id,))
    rows = cursor.fetchall()
    if rows:
        print(f"Mensagens do tópico {topic_id}:")
        for row in rows:
            print(f"ID: {row[0]}, Mensagem: {row[1]}, Timestamp: {row[2]}")
    else:
        print(f"Sem mensagens no tópico {topic_id}.")

# Exemplo de como usar
create_table()

# Adiciona uma mensagem ao banco de dados no tópico especificado
add_message(TOPIC, 'Esta é uma mensagem de teste 1.')
add_message(TOPIC, 'Esta é uma mensagem de teste 2.')

# Lista todas as mensagens do tópico especificado
list_messages_from_topic(TOPIC)

# Apaga todas as mensagens do tópico especificado
delete_all_messages_from_topic(TOPIC)

# Verifica se todas as mensagens foram deletadas
list_messages_from_topic(TOPIC)

# Fechar a conexão ao banco de dados
conn.close()