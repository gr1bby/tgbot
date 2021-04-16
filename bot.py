import config
import asyncio
import logging

from datetime import datetime
from multiprocessing import Process
from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQlighter

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()
db = SQlighter('db.db')
myid = config.my_id

@dp.message_handler(commands=['start'])
async def welcome_mess(message: types.Message):
    await message.reply("Hello! U r welcome!")

@dp.message_handler(commands=['help'])
async def help_mess(message: types.Message):
    await message.reply("It's help msge")


@dp.message_handler(commands=['subscribe'])
async def sub_msg(message: types.Message):
    if db.subscriber_exists(message.from_user.id):
        db.update_status(message.from_user.id, True)        
    else:
        db.add_subscriber(message.from_user.id)
    await bot.send_message(message.from_user.id, "Вы успешно подписались на рассылку!")

     
@dp.message_handler(commands=['unsubscribe'])
async def unsub_msg(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id, False)
        await bot.send_message(message.from_user.id, "Вы и так не подписаны")
    else:
        db.update_status(message.from_user.id, False)
        await bot.send_message(message.from_user.id, "Вы успешно отписались от рассылки")


async def msging(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        print("Rabotaet ")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        subs = db.get_subs()
        print(subs)

        for sub in subs:
            if current_time >= "08:31:00" and current_time < "08:31:10":
                await bot.send_message(sub[1], "sup")
                print(sub[1])

def loop_msg():
    loop.run_until_complete(msging(10))

if __name__ == '__main__':
    t = Process(target=loop_msg)
    t.start()
    executor.start_polling(dp, skip_updates=True)