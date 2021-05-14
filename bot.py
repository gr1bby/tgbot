import config
import keyboard as kb

import requests
import asyncio
import logging
import time
import pytz

from io import StringIO
from datetime import datetime, timedelta
from multiprocessing import Process

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from sqlighter import SQlighter

logging.basicConfig(level=logging.INFO)

# объявляем бота
bot = Bot(token=config.TOKEN)
# обращаемся к памяти для использования состояний
storage = MemoryStorage()
# объявляем диспатчер
dp = Dispatcher(bot, storage=storage)
# объявлям цикл
loop = asyncio.get_event_loop()
# создаем переменную для обращения к бд через класс
db = SQlighter('db.db')

class MyStates(StatesGroup):
    log_state = State() # состояние для обработки ввода логина
    date_state = State() # состояние для обработки ввода даты
    time_state = State() # состояние для обработки ввода времени

# приветствующая команда
@dp.message_handler(commands=['start'])
async def welcome_mess(message: types.Message):
    answ = "Вас приветствует хороший бот!\nДанный бот будет рассылать вам ваше расписание ГрГУ!\nЧтобы начать пользование, зарегистрируйтесь.\n"
    await bot.send_message(
        message.from_user.id,
        answ,
        reply_markup=kb.markup_unreg
    )

# описание всех команд
@dp.message_handler(commands=['help'])
async def help_mess(message: types.Message):
    if db.subscriber_exists(message.from_user.id):
        answ = "• /reg - Зарегистрироваться (Сменить логин)\n• /subscribe - Подписаться на рассылку\n• /unsubscribe - Отписаться от рассылки\n• /getschedule - Получить расписание по указанной дате\n• /changetime - Изменить время рассылки\n• /info - Показать информацию (логин, статус подписки, время автоматической рассылки)\n• /help - Посмотреть доступные команды\n"
        await bot.send_message(
            message.from_user.id, 
            answ, 
            reply_markup=kb.markup
        )
    else:
        answ = "Сперва пройдите регистрацию!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )

# проверяем наличие пользователя в бд и подписываем его на расссылку
@dp.message_handler(commands=['subscribe'])
async def sub_msg(message: types.Message):
    if db.subscriber_exists(message.from_user.id):
        db.update_status(message.from_user.id, True)      
        answ = "Вы успешно подписались на рассылку!"
        await bot.send_message(
            message.from_user.id, 
            answ,
            reply_markup=kb.markup
        )
    else:
        answ = "Сперва пройдите регистрацию!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )

# если пользователя нет в бд, то добавляем его уже отписанным, если есть, то просто отписываем
@dp.message_handler(commands=['unsubscribe'])
async def unsub_msg(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        answ = "Для чего вы отписываетесь?\nВы ведь даже не зарегистрированы!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )
    else:
        db.update_status(message.from_user.id, False)
        answ = "Вы успешно отписались от рассылки"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup
        )

# информация о пользователе
@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    if db.subscriber_exists(message.from_user.id):
        sub = db.get_sub(message.from_user.id)
        sub_login = sub[0][2]
        sub_time = sub[0][3]
        if sub[0][4]:
            sub_status = "подписка активирована✅"
        else:
            sub_status = "подписка не активирована❌"
        answ = f"• Ваш логин: {sub_login}☑\n• Ваш статус подписки: {sub_status}\n• Автоматическая рассылка заведена на {sub_time}🕑"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup
        )
    else:
        answ = "Сперва пройдите регистрацию!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )

# ввод команды регистрации, запрос логина и создание состояния
@dp.message_handler(commands=['reg'])
async def reg_msg(message: types.Message):
    await MyStates.log_state.set()

    await bot.send_message(message.from_user.id, "Введите ваш логин")      

# сообщение, введенное после запроса логина, будет тут обработано; так же добавляем новых пользователей в бд
@dp.message_handler(state=MyStates.log_state)
async def set_log(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        usr_login = data['text']
        
        if bool(check_login(usr_login)):
            if not db.subscriber_exists(message.from_user.id):
                db.add_subscriber(message.from_user.id)
            db.set_login(message.from_user.id, usr_login)
            answ_for_client = "Успешно!"
            await bot.send_message(
                message.from_user.id,
                answ_for_client,
                reply_markup=kb.markup
            )

        else:
            answ_for_client = "Неверный логин!"   
            await bot.send_message(
                message.from_user.id,
                answ_for_client,
                reply_markup=kb.markup_unreg
            )
 
    await state.finish()

# запрос даты
@dp.message_handler(commands=['getschedule'])
async def get_date(message: types.Message):
    await MyStates.date_state.set()

    if db.subscriber_exists(message.from_user.id):
        answ = "Введите дату\n(ДД.ММ.ГГГГ)"
        await bot.send_message(
            message.from_user.id,
            answ
        )
    else:
        answ = "Сперва пройдите регистрацию!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )

# установление даты и получение расписания по ней
@dp.message_handler(state=MyStates.date_state)
async def set_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        usr_date = data['text']

        sub = db.get_sub(message.from_user.id)

        login = sub[0][2]
        ID = get_studentID(login)
        schedule = get_schedule(ID, usr_date)

        if isinstance(schedule, str) and bool(schedule):
            answ = f"Расписание на {usr_date}:\n{schedule}"
        if isinstance(schedule, int):
            answ = "Неверный формат даты."
        if schedule == 0:
            answ = "В этот день нет занятий"
    
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup
        )

    await state.finish()

# запрос времени
@dp.message_handler(commands=['changetime'])
async def get_time(message: types.Message):
    await MyStates.time_state.set()

    if db.subscriber_exists(message.from_user.id):
        answ = "Введите время с точностью до минуты, в которое желаете получать расписание\n(напр. 07.47)"
        await bot.send_message(
            message.from_user.id,
            answ
        )
    else:
        answ = "Сперва пройдите регистрацию!\n(/reg)"
        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup_unreg
        )

# установка времени автоматической рассылки
@dp.message_handler(state=MyStates.time_state)
async def set_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        usr_time = data['text']

        try:
            time.strptime(usr_time, '%H.%M')
            if len(usr_time) == 5:
                db.set_time(message.from_user.id, usr_time)
                answ = "Время отправки успешно изменено"
            else:
                answ = "Неверный формат!"
        except Exception:
            answ = "Неверный формат!"

        await bot.send_message(
            message.from_user.id,
            answ,
            reply_markup=kb.markup
        )

    await state.finish()

# обработка кнопок и других текстовых сообщений пользователя
@dp.message_handler(content_types=['text'])
async def msg_asnw(message: types.Message):
    if message.text.lower() == "регистрация":
        await MyStates.log_state.set()

        await bot.send_message(message.from_user.id, "Введите ваш логин")
    
    elif message.text.lower() == "смена логина":
        await MyStates.log_state.set()

        await bot.send_message(message.from_user.id, "Введите ваш логин")

    elif message.text.lower() == "изменить время отправки":
        await MyStates.time_state.set()

        if db.subscriber_exists(message.from_user.id):
            answ = "Введите время с точностью до минуты, в которое желаете получать расписание\n(напр. 07.47)"
            await bot.send_message(
                message.from_user.id,
                answ
            )
        else:
            answ = "Сперва пройдите регистрацию!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )

    elif message.text.lower() == "подписаться на рассылку":
        if db.subscriber_exists(message.from_user.id):
            db.update_status(message.from_user.id, True)      
            answ = "Вы успешно подписались на рассылку!"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup
            )
        else:
            answ = "Сперва пройдите регистрацию!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )
   
    elif message.text.lower() == "отписаться от рассылки":
        if not db.subscriber_exists(message.from_user.id):
            answ = "Для чего вы отписываетесь?\nВы ведь даже не зарегистрированы!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )
        else:
            db.update_status(message.from_user.id, False)
            answ = "Вы успешно отписались от рассылки"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup
            ) 

    elif message.text.lower() == "расписание":
        await MyStates.date_state.set()

        if db.subscriber_exists(message.from_user.id):
            answ = "Введите дату\n(ДД.ММ.ГГГГ)"
            await bot.send_message(
                message.from_user.id,
                answ
            )
        else:
            answ = "Сперва пройдите регистрацию!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )
  
    elif message.text.lower() == "помощь":
        if db.subscriber_exists(message.from_user.id):
            answ = "• /reg - Зарегистрироваться (Сменить логин)\n• /subscribe - Подписаться на рассылку\n• /unsubscribe - Отписаться от рассылки\n• /getschedule - Получить расписание по указанной дате\n• /changetime - Изменить время рассылки\n• /info - Показать информацию (логин, статус подписки, время автоматической рассылки)\n• /help - Посмотреть доступные команды\n"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup
            )
        else:
            answ = "Сперва пройдите регистрацию!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )
    
    elif message.text.lower() == "инфо":
        if db.subscriber_exists(message.from_user.id):
            sub = db.get_sub(message.from_user.id)
            sub_login = sub[0][2]
            sub_time = sub[0][3]
            if sub[0][4]:
                sub_status = "подписка активирована✅"
            else:
                sub_status = "подписка не активирована❌"
            answ = f"• Ваш логин: {sub_login}☑\n• Ваш статус подписки: {sub_status}\n• Автоматическая рассылка заведена на {sub_time}🕑"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup
            )
        else:
            answ = "Сперва пройдите регистрацию!\n(/reg)"
            await bot.send_message(
                message.from_user.id,
                answ,
                reply_markup=kb.markup_unreg
            )
    
    else:
        await bot.send_message(
            message.from_user.id,
            "Не могу вас понять\nДля ознакомления с доступными командами введите /help",
            reply_markup=kb.markup_help
        )

# получаем ID студента
def get_studentID(login):
    try:
        r = requests.get(
            f"http://api.grsu.by/1.x/app2/getStudent?login={login}"
        )
        data = r.json()
        return data["id"]
    except Exception:
        pass

# получаем расписание
def get_schedule(ID, date):                 
    try:
        r = requests.get(
            f"http://api.grsu.by/1.x/app2/getGroupSchedule?studentId={ID}&dateStart={date}&dateEnd={date}"
        )
        data = r.json()

        try:
            if data["error"]["code"] == "24004" or data["error"]["code"] == "24005":
                error = int(data["error"]["code"])
                return error
        except Exception:
            pass

        try:
            if data["count"] == 0:
                return 0
        except Exception:
            pass

        count_of_lessons = data["days"][0]["count"]
        res = StringIO()
        for i in range(count_of_lessons):
            title = data["days"][0]["lessons"][i]["title"]
            typeOfLesn = data["days"][0]["lessons"][i]["type"]
            timeStart = data["days"][0]["lessons"][i]["timeStart"]
            teacher = data["days"][0]["lessons"][i]["teacher"]["fullname"]
            room = data["days"][0]["lessons"][i]["room"]
            address = data["days"][0]["lessons"][i]["address"]
            schedule = f"\n{timeStart}: {title} ({typeOfLesn});\n{teacher};\n{address}, {room}\n"
            res.write(schedule)
        return res.getvalue()
    except Exception as ex:
        print(ex)
        
# проверяем, существующий ли логин был введен
def check_login(login):
    if get_studentID(login) > 0:
        return True
    else:
        return False

# основной цикл бота, который рассылает расписание
async def msging(wait_for):
    while True:
        # устанавливаем задержку
        await asyncio.sleep(wait_for)
        # устанавливаем текущие дату и время
        tz = pytz.timezone('Europe/Minsk')
        now = datetime.now(tz)
        current_time = now.strftime("%H.%M")
        current_date = now.strftime("%d.%m.%Y")
        tomorrow_date = (now + timedelta(days=1)).strftime("%d.%m.%Y")
        # получаем всех пользователей с активной подпиской
        subs = db.get_subs()
        # делаем проверку на время, и, в случае совпадения, начинаем рассылать расписание
        for sub in subs:
            usr_time = sub[3]
            split_time = "15.00"
            if usr_time < split_time and current_time == usr_time:
                login = sub[2]
                ID = get_studentID(login)
                schedule = get_schedule(ID, current_date)
                if isinstance(schedule, str) and bool(schedule):
                    await bot.send_message(sub[1], f"Расписание на сегодня:\n{schedule}")
            elif usr_time >= split_time and current_time == usr_time:
                login = sub[2]
                ID = get_studentID(login)
                schedule = get_schedule(ID, tomorrow_date)
                if isinstance(schedule, str) and bool(schedule):
                    await bot.send_message(sub[1], f"Расписание на завтра:\n{schedule}")

# тут происходит объявление функции с основным циклом, для которой будет создан отдельный процесс
def loop_msg():
    loop.run_until_complete(msging(60))

if __name__ == '__main__':
    # объявляем и запускаем процесс для основного цикла
    t = Process(target=loop_msg)
    t.start()
    # запускаем бота
    executor.start_polling(dp, skip_updates=True)