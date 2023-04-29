import telebot
import json
import requests

url = "https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict"
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

API_TOKEN = '6273257931:AAEJDZpOyZOQfHLbRyBmCF4SP7HQaTCeaS8'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True)
def json_response(message):
    text = message.text
    data = {
        "instances": [
            {
                "text": text,
                "num_beams": 5,
                "num_return_sequences": 3,
                "length_penalty": 0.5
            }
        ]
    }
    print(data)
    response = requests.post(url, headers=headers, data=json.dumps(data))
    #print(response.status_code)
    #print(response.json())
    parsed_response = response.json()
    origin_answer = parsed_response['origin']
    best_answer = parsed_response['prediction_best']['bertscore']
    print(best_answer)
    print(origin_answer)
    bot.send_message(message.chat.id, f"{best_answer}")




# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
"""@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, json_response())"""


bot.infinity_polling()
