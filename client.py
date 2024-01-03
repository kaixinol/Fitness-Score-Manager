import requests
import os

from rich.console import Console
from rich.table import Table

print('请登录！')
username = input('用户名：')
password = input('密码：')


class Query:
    def __init__(self, username, password, host='127.0.0.1', port=5000):
        self.__username = username
        self.__password = password
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/"
        self.base_data = {'username': self.__username, 'password': self.__password}

    def find(self, name: str):
        data = requests.get(self.base_url + "/data",
                            data={**self.base_data, 'account_name': name})
        if data.status_code in [404, 403]:
            print(data.text)
            return
        table = Table()
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        table.add_row(*[str(l) for l in data.json()])
        Console().print(table)

    def add(self, name: str, **kwargs):
        print(requests.post(self.base_url + "/data",
                            data={**self.base_data, 'account_name': name, **kwargs}).text)

    def update(self, name: str, **kwargs):
        print(requests.put(self.base_url + "/data",
                           data={**self.base_data, 'account_name': name, **kwargs}).text)

    def delete(self, name: str):
        response = requests.delete(self.base_url + "/data",
                                   data={**self.base_data, 'account_name': name})
        if response.status_code == 200:
            print(response.text)
        else:
            print(response.text)

    def show_all(self):
        data = requests.get(self.base_url + "/get_all_data", data=self.base_data)
        if data.status_code == 401:
            print(data.text)
            return
        table = Table()
        table.add_column('学号')
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        for i in data.json():
            table.add_row(*[str(l) for l in i])
        Console().print(table)

    def show_failing_grade(self):
        data = requests.get(self.base_url + "/get_all_data", data=self.base_data).json()
        result: list = []
        for i in data:
            student_id, push_ups, sit_ups, pull_ups, run_3000m = i
            if push_ups < 10:
                push_ups = f'{push_ups}(不及格)'
            else:
                push_ups = str(push_ups)
            if sit_ups < 20:
                sit_ups = f'{sit_ups}(不及格)'
            else:
                sit_ups = str(sit_ups)
            if pull_ups < 3:
                pull_ups = f'{pull_ups}(不及格)'
            else:
                pull_ups = str(pull_ups)
            if run_3000m < 15 * 60:
                run_3000m = f'{run_3000m}(不及格)'
            else:
                run_3000m = str(run_3000m)
            result.append([student_id, push_ups, sit_ups, pull_ups, run_3000m])
        table = Table()
        table.add_column('学号')
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        for i in result:
            table.add_row(*i)
        Console().print(table)


def clear_console():
    # 根据操作系统不同执行相应的清空命令
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS 和 Linux
        os.system('clear')


query = Query(username, password)
while True:
    print('1. 查 2. 增 3. 改 4. 删  5. 全部显示 6. 显示不及格\n其他键退出')
    match input():
        case '1':
            clear_console()
            query.find(input('学号：'))
        case '2':
            clear_console()
            query.add(input('学号：'), push_ups=input('俯卧撑：'), sit_ups=input('仰卧起坐：'),
                      pull_ups=input('引体向上：'), run_3000m=input('3000米跑：'))
        case '3':
            clear_console()
            query.update(input('学号：'), push_ups=input('俯卧撑：'), sit_ups=input('仰卧起坐：'),
                         pull_ups=input('引体向上：'), run_3000m=input('3000米跑：'))
        case '4':
            clear_console()
            query.delete(input('学号：'))
        case '5':
            clear_console()
            query.show_all()
        case '6':
            clear_console()
            query.show_failing_grade()
        case _:
            break
