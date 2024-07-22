import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
from bs4 import BeautifulSoup
import requests
import telebot
from telebot import types
bot = telebot.TeleBot('')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button = types.KeyboardButton('meme')
    markup.add(button)
    bot.send_message(message.chat.id,'Hello,enter /meme or press the button to receive a random meme from reddit',reply_markup=markup)
    bot.register_next_step_handler(message,parser)



def parser(message):
    if message.text.lower() == 'meme':
        bot.send_message(message.chat.id,'Wait,It takes some time....')
        options = Options()
        options.add_argument("start-maximized")
        service = Service(r'webdriver/chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)

        try:
            subreddits = ['dankmemes', 'memes', 'meme', 'Memes_Of_The_Dank', 'MoldyMemes', 'Animemes']
            random_subreddit = random.choice(subreddits)
            url = f'https://www.reddit.com/r/{random_subreddit}/'
            driver.get(url)
            html = driver.page_source

            # Create directory if it doesn't exist
            os.makedirs(random_subreddit, exist_ok=True)

            html_file_path = os.path.join(random_subreddit, f'{random_subreddit}.html')

            with open(html_file_path, 'w', encoding='utf-8') as file:
                file.write(html)

            with open(html_file_path, encoding='utf-8') as file:
                src = file.read()

            soup = BeautifulSoup(src, 'lxml')
            shreddit_app = soup.find('shreddit-app')
            articles = shreddit_app.find_all(class_='w-full m-0')
            shreddit_post = articles[1]
            post_title = shreddit_post.find('a').find('faceplate-screen-reader-content').text.strip()
            image = shreddit_post.find('img')
            image_url = image['src']


            valid_post_title = ''.join(c for c in post_title if c.isalnum() or c in (' ', '_')).rstrip()
            image_file_path = os.path.join(random_subreddit, f'{valid_post_title}.jpeg')

            image_response = requests.get(image_url)
            with open(image_file_path, 'wb') as file:
                file.write(image_response.content)

            if post_title and image_response:
                bot.send_photo(message.chat.id,image_response.content,caption=post_title)
                bot.register_next_step_handler(message,parser)
        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()
    else:
        bot.send_message(message.chat.id, 'Please press the "meme" button or type /meme.')
bot.polling(none_stop=True)