from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from telebot import types
from time import gmtime
import feedparser
import os
import re
import telebot
import telegraph
import time
import random
import requests
import sqlite3

def get_variable(variable):
    """Obtém variáveis do ambiente ou arquivos locais."""
    if not os.environ.get(f'{variable}'):
        with open(f'{variable}.txt', 'r') as var_file:
            return var_file.read().strip()
    return os.environ.get(f'{variable}')

URL = get_variable('URL')
DESTINATION = get_variable('DESTINATION')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
EMOJIS = os.environ.get('EMOJIS', '🗞,📰,🗒,🗓,📋,🔗,📝,🗃')
DRYRUN = os.environ.get('DRYRUN')

bot = telebot.TeleBot(BOT_TOKEN)

def add_to_history(link):
    """Adiciona um link ao histórico para evitar mensagens duplicadas."""
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS history (link TEXT)')
    cursor.execute('INSERT INTO history (link) VALUES (?)', (link,))
    conn.commit()
    conn.close()

def check_history(link):
    """Verifica se o link já foi enviado."""
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS history (link TEXT)')
    cursor.execute('SELECT * FROM history WHERE link=?', (link,))
    data = cursor.fetchone()
    conn.close()
    return data

def extract_image_from_description(description):
    """Extrai a URL da imagem da tag <description>."""
    try:
        img_tag = re.search(r'<img src="(.*?)"', description)
        if img_tag:
            return img_tag.group(1)  # Retorna a URL da imagem
    except TypeError:
        pass
    return None  # Retorna None caso não encontre uma imagem

def extract_topic_data(item):
    """Extrai os dados necessários de cada item do feed RSS."""
    try:
        title = item.find('title').text
        link = item.find('link').text
        author = item.find('dc:creator').text if item.find('dc:creator') else "Desconhecido"
        description = item.find('description').text

        # Extrair imagem da descrição
        image = extract_image_from_description(description)

        return {
            'title': title.strip(),
            'link': link.strip(),
            'author': author.strip(),
            'photo': image
        }
    except AttributeError as e:
        print(f"Erro ao extrair dados do item: {e}")
        return None

def send_message(topic, button_text):
    """Envia a mensagem formatada para o Telegram com imagem, título e botão."""
    if DRYRUN == 'failure':
        return

    MESSAGE_TEMPLATE = f"<b>{topic['title']}</b>\n\nPor: {topic['author']}\n<a href='{topic['link']}'>Acesse o post completo</a>"
    btn_link = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(button_text, url=topic['link'])
    btn_link.row(btn)

    for dest in DESTINATION.split(','):
        if topic['photo']:
            try:
                response = requests.get(topic['photo'], headers={'User-agent': 'Mozilla/5.1'})
                with open('img.jpg', 'wb') as f:
                    f.write(response.content)
                
                with open('img.jpg', 'rb') as photo:
                    bot.send_photo(
                        dest,
                        photo,
                        caption=MESSAGE_TEMPLATE,
                        parse_mode='HTML',
                        reply_markup=btn_link
                    )
            except telebot.apihelper.ApiTelegramException as e:
                print(f'Erro ao enviar imagem: {e}')
                bot.send_message(
                    dest,
                    MESSAGE_TEMPLATE,
                    parse_mode='HTML',
                    reply_markup=btn_link
                )
        else:
            bot.send_message(
                dest,
                MESSAGE_TEMPLATE,
                parse_mode='HTML',
                reply_markup=btn_link
            )
        print(f'Mensagem enviada: {topic[\'title\']}')
    time.sleep(0.2)

def process_feed(feed_url):
    """Processa o feed RSS, extrai os dados e envia mensagens."""
    response = requests.get(feed_url)
    soup = BeautifulSoup(response.content, 'xml')  # Usando BeautifulSoup para processar XML
    items = soup.find_all('item')  # Extrai todos os itens do feed

    for item in items:
        topic = extract_topic_data(item)
        if not topic:
            continue  # Ignora itens com erro na extração

        if check_history(topic['link']):
            print(f"Mensagem já enviada: {topic['title']}")
            continue

        add_to_history(topic['link'])
        BUTTON_TEXT = f"Leia mais de {topic['author']}"
        send_message(topic, BUTTON_TEXT)

if __name__ == "__main__":
    for url in URL.split():
        process_feed(url)
