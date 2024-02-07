import telebot
import openai
import requests
import time
import docx
import tempfile

openai.api_key = "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"

# инициализируем бота с помощью токена
bot = telebot.TeleBot("6103475049:AAGIunWgjky8EPlKlI-oL5iGKV4-BdDgAjo")

chunk_size = 1500
overlap_size = 100

def decode_docx(file_path):
    doc = docx.Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

# ПИНГ БОТА
@bot.message_handler(commands=['p'])
def ping(message):
    bot.send_message(message.chat.id, 'Работаю')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """\
Привет, я бот-суммаризатор, я умею сжимать любой текст. Для этого вставь сюда текст, который хочешь сжать\
""")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """\
За помощью обращайся к моему создателю, а кто он - я тебе не скажу\
""")

# обработчик команды /sum
@bot.message_handler(func=lambda message: True)
def summarize_text(message):
    # проверяем, что сообщение не является командой и не является пустым
    if message.text is None or message.text.startswith('/'):
        return
    

    # получаем текст из сообщения пользователя
    text = message.text.strip()
    
    if text in ["Пидор", "Пидр"]:
        bot.reply_to(message, """Сам такой!""")
    # проверяем, что текст не пустой и проверяем, что текст не превышает максимальную длину
    elif len(text) <= 100:
        bot.send_message(message.chat.id, "Введите корректный текст.")
        return
    elif len(text) > 5000:
        bot.send_message(message.chat.id, "Текст превышает максимальную длину.")
        return
    else:

        # разбиваем текст на чанки
        chunks = [text[i:i + chunk_size - overlap_size] for i in range(0, len(text), chunk_size - overlap_size)]
    
        # обрабатываем каждый чанк с помощью OpenAI API и отправляем ответ на каждый чанк
        summaries = []
        bot.send_message(message.chat.id, f"Ваш текст будет обрабатываться {len(chunks)*20} секунд, пожалуйста подождите.")
        for i, chunk in enumerate(chunks):
            prompt_request = "Обобщи текст выделяя главное: " + chunk
            messages = [{"role": "system", "content": "Это суммаризатор текста и переводчик этого текста на русский язык"}]
            messages.append({"role": "user", "content": prompt_request})
    
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=.5,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
    
            summary = response["choices"][0]["message"]['content'].strip()
            summaries.append(summary)
            time.sleep(20)
    
        # объединяем суммаризации чанков в один ответ
        final_summary = " ".join(summaries)
        final_summary = final_summary.split('.', 1)[-1].strip()
        bot.send_message(message.chat.id, final_summary)


@bot.message_handler(content_types=['document'])
def summarize_document(message):

    # получаем информацию о файле
    file_info = bot.get_file(message.document.file_id)
    # скачиваем файл
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, file_info.file_path))

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.content)
        temp_file_path = temp_file.name
    # декодируем содержимое файла из байтов в текст
    text = decode_docx(temp_file_path)

    # проверяем, что текст не пустой и проверяем, что текст не превышает максимальную длину
    if not text:
        bot.send_message(message.chat.id, "Файл пустой.")
        return

    # разбиваем текст на чанки
    chunks = [text[i:i + chunk_size - overlap_size] for i in range(0, len(text), chunk_size - overlap_size)]

    # обрабатываем каждый чанк с помощью OpenAI API и отправляем ответ на каждый чанк
    summaries = []
    bot.send_message(message.chat.id,
                     f"Ваш текст будет обрабатываться {len(chunks) * 20} секунд, пожалуйста подождите.")
    for i, chunk in enumerate(chunks):
        prompt_request = "Обобщи текст выделяя главное: " + chunk
        messages = [{"role": "system", "content": "Это суммаризатор текста и переводчик этого текста на русский язык"}]
        messages.append({"role": "user", "content": prompt_request})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=.5,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        summary = response["choices"][0]["message"]['content'].strip()
        summaries.append(summary)
        time.sleep(20)

    # объединяем суммаризации чанков в один ответ
    final_summary = " ".join(summaries)
    final_summary = final_summary.split('.', 1)[-1].strip()
    bot.send_message(message.chat.id, final_summary)


# запускаем бота
bot.infinity_polling()
