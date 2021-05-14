from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button_reg = "Регистрация"
button_change = "Смена логина"
button_time = "Изменить время отправки"
button_sub = "Подписаться на рассылку"
button_unsub = "Отписаться от рассылки"
button_sd = "Расписание"
button_help = "Помощь"
button_info = "Инфо"

markup_unreg = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup_help = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

markup_unreg.add(button_reg)

markup_help.add(button_help)

markup.add(button_change, button_time)
markup.add(button_sub, button_unsub)
markup.add(button_sd)
markup.add(button_help, button_info)