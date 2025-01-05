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
    if not os.environ.get(f'{variable}'):
        var_file = open(f'{variable}.txt', 'r')
        return var_file.read().strip()
    return os.environ.get(f'{variable}')

URL = get_variable('URL')
DESTINATION = get_variable('DESTINATION')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
EMOJIS = os.environ.get('EMOJIS', '🗞,📰,🗒,🗓,📋,🔗,📝,🗃')
HIDE_BUTTON = os.environ.get('HIDE_BUTTON', False)
DRYRUN = os.environ.get('DRYRUN')

bot = telebot.TeleBot(BOT_TOKEN)

def add_to_history(link):
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO history (link) VALUES (?)', (link,))
    conn.commit()
    conn.close()

def check_history(link):
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * from history WHERE link=?', (link,))
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

def send_message(topic, button_text):
    """Envia a mensagem para o Telegram."""
    if DRYRUN == 'failure':
        return

    MESSAGE_TEMPLATE = os.environ.get('MESSAGE_TEMPLATE', False)
    if MESSAGE_TEMPLATE:
        MESSAGE_TEMPLATE = set_text_vars(MESSAGE_TEMPLATE, topic)
    else:
        MESSAGE_TEMPLATE = f'<b>{topic["title"]}</b>\n{topic["link"]}'

    btn_link = None
    if button_text:
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
                    bot.send_photo(dest, photo, caption=MESSAGE_TEMPLATE, parse_mode='HTML', reply_markup=btn_link)
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(dest, MESSAGE_TEMPLATE, parse_mode='HTML', reply_markup=btn_link)
        else:
            bot.send_message(dest, MESSAGE_TEMPLATE, parse_mode='HTML', reply_markup=btn_link)
        print(f'Mensagem enviada: {topic["title"]}')
    time.sleep(0.2)

def set_text_vars(text, topic):
    """Substitui variáveis no template de mensagem."""
    cases = {
        'SITE_NAME': topic['site_name'],
        'TITLE': topic['title'],
        'LINK': topic['link'],
        'EMOJI': random.choice(EMOJIS.split(","))
    }
    for word in re.split('{|}', text):
        try:
            text = text.replace(word, cases.get(word, word))
        except TypeError:
            continue
    return text.replace('\\n', '\n')

def check_topics(url):
    """Verifica os tópicos no feed RSS."""
    feed = feedparser.parse(url)
    try:
        source = feed['feed']['title']
    except KeyError:
        print(f'\nERRO: {url} não parece um feed RSS válido.')
        return

    print(f'\nChecando {source}:{url}')
    for item in reversed(feed['items'][:10]):  # Processar os 10 itens mais recentes
        link = item.link
        if check_history(link):
            continue

        add_to_history(link)

        # Criar o objeto `topic` com os dados desejados
        topic = {
            'site_name': source,
            'title': item.title.strip(),
            'link': link,
            'photo': extract_image_from_description(item.description),  # Extrai a imagem
        }

        BUTTON_TEXT = os.environ.get('BUTTON_TEXT', False)
        if BUTTON_TEXT:
            BUTTON_TEXT = set_text_vars(BUTTON_TEXT, topic)

        try:
            send_message(topic, BUTTON_TEXT)
        except telebot.apihelper.ApiTelegramException as e:
            print(f'Erro ao enviar mensagem: {e}')

if __name__ == "__main__":
    for url in URL.split():
        check_topics(url)
