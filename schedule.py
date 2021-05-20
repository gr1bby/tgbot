import requests
from io import StringIO

class Schedule:
    # получаем ID студента
    @staticmethod
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
    @staticmethod
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
    @staticmethod
    def check_login(get_studentID, login):
        if get_studentID(login) > 0:
            return True
        else:
            return False