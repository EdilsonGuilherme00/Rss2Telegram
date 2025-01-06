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
        return var_file.read()
    return os.environ.get(f'{variable}')

URL = get_variable('URL')
DESTINATION = get_variable('DESTINATION')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
EMOJIS = os.environ.get('EMOJIS', '🗞,📰,🗒,🗓,📋,🔗,📝,🗃')
PARAMETERS = os.environ.get('PARAMETERS', False)
HIDE_BUTTON = os.environ.get('HIDE_BUTTON', False)
DRYRUN = os.environ.get('DRYRUN')
TOPIC = os.environ.get('TOPIC', False)
TELEGRAPH_TOKEN = os.environ.get('TELEGRAPH_TOKEN', False)

bot = telebot.TeleBot(BOT_TOKEN)

def add_to_history(link):
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    aux = f'INSERT INTO history (link) VALUES ("{link}")'
    cursor.execute(aux)
    conn.commit()
    conn.close()

def check_history(link):
    conn = sqlite3.connect('rss2telegram.db')
    cursor = conn.cursor()
    aux = f'SELECT * from history WHERE link="{link}"'
    cursor.execute(aux)
    data = cursor.fetchone()
    conn.close()
    return data

def firewall(text):
    try:
        rules = open(f'RULES.txt', 'r')
    except FileNotFoundError:
        return True
    result = None
    for rule in rules.readlines():
        opt, arg = rule.split(':')
        arg = arg.strip()
        if arg == 'ALL' and opt == 'DROP':
            result = False
        elif arg == 'ALL' and opt == 'ACCEPT':
            result = True
        elif arg.lower() in text.lower() and opt == 'DROP':
            result = False
        elif arg.lower() in text.lower() and opt == 'ACCEPT':
            result = True
    return result

def create_telegraph_post(topic):
    telegraph_auth = telegraph.Telegraph(
        access_token=f'{get_variable("TELEGRAPH_TOKEN")}'
    )
    response = telegraph_auth.create_page(
        f'{topic["title"]}',
        html_content=(
            f'{topic["summary"]}<br><br>'
            + f'<a href="{topic["link"]}">Ver original ({topic["site_name"]})</a>'
        ),
        author_name=f'{topic["site_name"]}'
    )
    return response["url"]
def send_message(topic, button_text):
    if DRYRUN == 'failure':
        return

    MESSAGE_TEMPLATE = os.environ.get('MESSAGE_TEMPLATE', False)

    if MESSAGE_TEMPLATE:
        MESSAGE_TEMPLATE = set_text_vars(MESSAGE_TEMPLATE, topic)
    else:
        MESSAGE_TEMPLATE = f'<b>{topic["title"]}</b>\n\n{topic["summary"]}'

    # Criar botão inline com o link
    if button_text:
        btn_link = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(button_text, url=topic['link'])
        btn_link.row(btn)
    else:
        btn_link = None

    # Enviar a mensagem
    for dest in DESTINATION.split(','):
        if topic['photo']:
            try:
                # Baixar imagem para enviar
                response = requests.get(topic['photo'], headers={'User-agent': 'Mozilla/5.1'})
                with open('img', 'wb') as img_file:
                    img_file.write(response.content)

                with open('img', 'rb') as photo:
                    bot.send_photo(dest, photo, caption=MESSAGE_TEMPLATE, parse_mode='HTML', reply_markup=btn_link)
            except Exception as e:
                print(f"Erro ao enviar imagem: {e}")
        else:
            bot.send_message(dest, MESSAGE_TEMPLATE, parse_mode='HTML', reply_markup=btn_link)
    
    print(f'Mensagem enviada: {topic["title"]}')
    time.sleep(0.2)

def get_img_from_feed(item):
    """Extrai a imagem do campo <description> do feed RSS."""
    try:
        soup = BeautifulSoup(item.description, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
    except Exception as e:
        print(f"Erro ao extrair imagem: {e}")
    return None

def define_link(link, PARAMETERS):
    if PARAMETERS:
        if '?' in link:
            return f'{link}&{PARAMETERS}'
        return f'{link}?{PARAMETERS}'
    return f'{link}'

def set_text_vars(text, topic):
    cases = {
        'SITE_NAME': topic['site_name'],
        'TITLE': topic['title'],
        'SUMMARY': re.sub('<[^<]+?>', '', topic['summary']),
        'LINK': define_link(topic['link'], PARAMETERS),
        'EMOJI': random.choice(EMOJIS.split(","))
    }
    for word in re.split('{|}', text):
        try:
            text = text.replace(word, cases.get(word))
        except TypeError:
            continue
    return text.replace('\\n', '\n').replace('{', '').replace('}', '')

def check_topics(url):
    now = gmtime()
    feed = feedparser.parse(url)
    try:
        source = feed['feed']['title']
    except KeyError:
        print(f'\nERRO: {url} não parece um feed RSS válido.')
        return
    print(f'\nChecando {source}:{url}')
    for tpc in reversed(feed['items'][:10]):
        if check_history(tpc.links[0].href):
            continue
        add_to_history(tpc.links[0].href)
        topic = {
            'site_name': feed['feed']['title'],
            'title': tpc.title.strip(),
            'summary': tpc.summary,
            'link': tpc.links[0].href,
            'photo': get_img_from_feed(tpc),
        }
        BUTTON_TEXT = "🔗 Acesse o Post"
        try:
            send_message(topic, BUTTON_TEXT)
        except telebot.apihelper.ApiTelegramException as e:
            print(e)
            pass

if __name__ == "__main__":
    for url in URL.split():
        check_topics(url)
