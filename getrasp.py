import requests
from pprint import pprint

def get_schedule(ID):
    try:
        r = requests.get(
            f"http://api.grsu.by/1.x/app2/getGroupSchedule?studentId={ID}&dateStart=13.04.2021&dateEnd=13.04.2021"
        )
        data = r.json()
        pprint(data)
        pprint(data["days"][0]["lessons"][2]["room"])
    except Exception as ex:
        print(ex)

def get_studentID(login):
    try:
        r = requests.get(
            f"http://api.grsu.by/1.x/app2/getStudent?login={login}"
        )
        data = r.json()
        return data["id"]
    except Exception as ex:
        print(ex) 

def main():
    #login = input("Input login: ")
    login = "veselov_aa_19"
    ID = get_studentID(login)
    get_schedule(ID)

if __name__ == "__main__":
    main()