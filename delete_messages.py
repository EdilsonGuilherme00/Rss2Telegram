import sqlite3
import os
from datetime import datetime, timedelta
import pytz

# Configuração do fuso horário
LOCAL_TIMEZONE = pytz.timezone('America/Sao_Paulo')

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
    # Captura o horário local e converte para UTC antes de salvar
    now_utc = datetime.now(pytz.utc)
    cursor.execute('INSERT INTO messages (topic_id, message, timestamp) VALUES (?, ?, ?)', 
                   (topic_id, message, now_utc.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()

# Função para apagar mensagens de um tópico específico após 24 horas
def delete_messages_from_topic(topic_id):
    # Calcula a data de corte em UTC
    cutoff_time = datetime.now(pytz.utc) - timedelta(hours=24)
    cutoff_time_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Deletando mensagens do tópico {topic_id} com timestamp anterior a: {cutoff_time_str}")
    
    # Comparação correta usando o formato DATETIME do SQLite
    cursor.execute('DELETE FROM messages WHERE topic_id = ? AND timestamp < ?', (topic_id, cutoff_time_str))
    conn.commit()

# Exemplo de como usar
create_table()

# Adiciona uma mensagem ao banco de dados no tópico especificado
add_message(TOPIC, 'Esta é uma mensagem de teste.')

# Apaga mensagens do tópico especificado após 24 horas
delete_messages_from_topic(TOPIC)

# Fechar a conexão ao banco de dados
conn.close()
