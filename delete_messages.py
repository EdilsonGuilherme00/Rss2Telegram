import sqlite3

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
    print(f"Mensagem adicionada ao tópico {topic_id}.")

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

# Função para deletar todas as mensagens de um tópico específico
def delete_all_messages_from_topic(topic_id):
    cursor.execute('DELETE FROM messages WHERE topic_id = ?', (topic_id,))
    conn.commit()
    print(f"Todas as mensagens do tópico {topic_id} foram deletadas.")

# Exibir menu de opções
def menu():
    print("\nComandos disponíveis:")
    print("1 - Adicionar mensagem")
    print("2 - Listar mensagens de um tópico")
    print("3 - Deletar todas as mensagens de um tópico")
    print("4 - Sair")

# Inicialização
create_table()

# Loop para comandos do usuário
while True:
    menu()
    choice = input("\nEscolha uma opção: ")

    if choice == "1":
        try:
            topic_id = int(input("Digite o ID do tópico: "))
            message = input("Digite a mensagem: ")
            add_message(topic_id, message)
        except ValueError:
            print("Por favor, insira um ID de tópico válido.")

    elif choice == "2":
        try:
            topic_id = int(input("Digite o ID do tópico: "))
            list_messages_from_topic(topic_id)
        except ValueError:
            print("Por favor, insira um ID de tópico válido.")

    elif choice == "3":
        try:
            topic_id = int(input("Digite o ID do tópico: "))
            delete_all_messages_from_topic(topic_id)
        except ValueError:
            print("Por favor, insira um ID de tópico válido.")

    elif choice == "4":
        print("Saindo...")
        break

    else:
        print("Opção inválida. Tente novamente.")

# Fechar conexão com o banco de dados
conn.close()
