import telebot
import openai
import requests

openai.api_key = ""

# инициализируем бота с помощью токена
bot = telebot.TeleBot("")

chunk_size = 1500
overlap_size = 100


# ПИНГ БОТА
@bot.message_handler(commands=['p'])
def ping(message):
    bot.send_message(message.chat.id, 'Работаю')


# обработчик команды /sum
@bot.message_handler(func=lambda message: True)
def summarize_text(message):
    # проверяем, что сообщение не является командой и не является пустым
    if message.text is None or message.text.startswith('/'):
        bot.send_message(message.chat.id, "Введите текст для суммаризации.")
        return

    # получаем текст из сообщения пользователя
    text = message.text.strip()

    # проверяем, что текст не пустой и проверяем, что текст не превышает максимальную длину
    if len(text) == 0:
        bot.send_message(message.chat.id, "Введите текст для суммаризации.")
        return
    elif len(text) > 5000:
        bot.send_message(message.chat.id, "Текст превышает максимальную длину.")
        return

    # разбиваем текст на чанки
    chunks = [text[i:i + chunk_size - overlap_size] for i in range(0, len(text), chunk_size - overlap_size)]

    # обрабатываем каждый чанк с помощью OpenAI API и отправляем ответ на каждый чанк
    summaries = []
    for i, chunk in enumerate(chunks):
        prompt_request = "Обобщи текст выделяя главное: " + chunk

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_request,
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        summary = response.choices[0].text.strip()
        summaries.append(summary)

    # объединяем суммаризации чанков в один ответ
    final_summary = " ".join(summaries)
    final_summary = final_summary.split('.', 1)[-1].strip()
    bot.send_message(message.chat.id, final_summary)


@bot.message_handler(content_types=['doc'])
def summarize_document(message):

    # получаем информацию о файле
    file_info = bot.get_file(message.document.file_id)
    # скачиваем файл
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, file_info.file_path))
    # декодируем содержимое файла из байтов в текст
    text = file.content.decode('utf-8')

    # проверяем, что текст не пустой и проверяем, что текст не превышает максимальную длину
    if not text:
        bot.send_message(message.chat.id, "Файл пустой.")
        return

    # разбиваем текст на чанки
    chunks = [text[i:i + chunk_size - overlap_size] for i in range(0, len(text), chunk_size - overlap_size)]

    # обрабатываем каждый чанк с помощью OpenAI API
    summaries = []
    for i, chunk in enumerate(chunks):
        prompt_request = "Обобщи текст используя цитаты из оригинального текста: " + chunk

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_request,
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        summary = response.choices[0].text.strip()
        summaries.append(summary)

    # объединяем суммаризации чанков в один ответ
    final_summary = " ".join(summaries)
    bot.send_message(message.chat.id, final_summary)


# запускаем бота
bot.polling()
