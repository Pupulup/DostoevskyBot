import aiogram
from aiogram import Bot, Dispatcher, executor, types
from secret_info import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\n Пришлите текст, который хотите сжать")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
