import sqlite3

class SQlighter:
    # устанавливаем соединение с базой данных
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # добавляем саба для рассылки
    def add_subscriber(self, user_id, status=True):
        with self.connection:
            return self.cursor.execute("INSERT INTO subs (user_id, status) VALUES (?,?)", (user_id, status))

    # обнавляем статус подписки
    def update_status(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE subs SET status = ? WHERE user_id = ?", (status, user_id))

    # проверяем, есть ли юзер в бд
    def subscriber_exists(self, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM subs WHERE user_id = ?", (user_id,)).fetchall()))

    # получаем всех активных пользователей
    def get_subs(self, status=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM subs WHERE status = ?", (status,)).fetchall()

    # получаем данные пользователя по запросу
    def get_sub(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM subs WHERE user_id = ?", (user_id,)).fetchall()

    # устанавливаем логин для пользователя
    def set_login(self, user_id, user_login, status = True):
        with self.connection:
            return self.cursor.execute("UPDATE subs SET user_login = ?, status = ? WHERE user_id = ?",(user_login, status, user_id))
    
    # устанавливаем время рассылки пользователя
    def set_time(self, user_id, user_time):
        with self.connection:
            return self.cursor.execute("UPDATE subs SET user_time = ? WHERE user_id = ?",(user_time, user_id))

    # закрываем соединение
    def close(self):
        self.connection.close()