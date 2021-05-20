from aiogram.dispatcher.filters.state import State, StatesGroup

class MyStates(StatesGroup):
    log_state = State() # состояние для обработки ввода логина
    date_state = State() # состояние для обработки ввода даты
    time_state = State() # состояние для обработки ввода времени