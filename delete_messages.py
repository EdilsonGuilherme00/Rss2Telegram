import sqlite3
import os

# Obtendo variáveis de ambiente
TOPIC = os.getenv('TOPIC')
if TOPIC is None:
    print("TOPIC não está definido no ambiente.")
    TOPIC = "1"  # Valor padrão para fins de teste
else:
    print(f"TOPIC: {TOPIC}")

# Certifique-se de que TOPIC seja tratado como inteiro
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

# Função para deletar todas as mensagens de um tópico específico
def delete_messages_by_topic(topic_id):
    print(f"Deletando todas as mensagens do tópico {topic_id}...")
    cursor.execute('DELETE FROM messages WHERE topic_id = ?', (topic_id,))
    conn.commit()
    print(f"Mensagens do tópico {topic_id} foram deletadas.")

# Uso direto:
create_table()

# Aqui chamamos a função para deletar as mensagens do tópico especificado
delete_messages_by_topic(TOPIC)

# Fechar a conexão ao banco de dados
conn.close()
