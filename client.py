import requests
import os
from rich.console import Console
from rich.table import Table

console = Console()

print('请登录！')
username = input('用户名：')
password = input('密码：')


class Query:
    def __init__(self, username, password, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self._login(username, password)

    def _login(self, username, password):
        response = self.session.post(f"{self.base_url}/signin", json={'username': username, 'password': password})
        if response.status_code == 200:
            console.print("[green]登录成功！[/green]")
        else:
            console.print(f"[red]登录失败：{response.text}[/red]")
            exit(1)

    def find(self, name: str):
        response = self.session.get(f"{self.base_url}/data", params={'account_name': name})
        if response.status_code in [404, 403, 401]:
            console.print(f"[red]{response.text}[/red]")
            return
        data = response.json()
        table = Table(title="学生成绩")
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        table.add_row(*[str(d) for d in data])
        console.print(table)

    def add(self, name: str, **kwargs):
        response = self.session.post(f"{self.base_url}/data", json={'account_name': name, **kwargs})
        console.print(response.text)

    def update(self, name: str, **kwargs):
        response = self.session.put(f"{self.base_url}/data", json={'account_name': name, **kwargs})
        console.print(response.text)

    def delete(self, name: str):
        response = self.session.delete(f"{self.base_url}/data", params={'account_name': name})
        console.print(response.text)

    def show_all(self):
        response = self.session.get(f"{self.base_url}/get_all_data")
        if response.status_code != 200:
            console.print(f"[red]{response.text}[/red]")
            return
        data = response.json()
        table = Table(title="所有学生成绩")
        table.add_column('学号')
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        for record in data:
            table.add_row(*[str(item) for item in record])
        console.print(table)

    def show_failing_grade(self):
        response = self.session.get(f"{self.base_url}/get_all_data")
        if response.status_code != 200:
            console.print(f"[red]{response.text}[/red]")
            return
        data = response.json()
        result = []
        for student_id, push_ups, sit_ups, pull_ups, run_3000m in data:
            run_minutes = float(run_3000m) / 60
            push_ups = f'{push_ups}(不及格)' if push_ups < 10 else str(push_ups)
            sit_ups = f'{sit_ups}(不及格)' if sit_ups < 20 else str(sit_ups)
            pull_ups = f'{pull_ups}(不及格)' if pull_ups < 3 else str(pull_ups)
            run_3000m = f'{run_minutes:.2f}分钟(不及格)' if run_minutes > 15 else f'{run_minutes:.2f}分钟'
            result.append([student_id, push_ups, sit_ups, pull_ups, run_3000m])
        table = Table(title="不及格学生成绩")
        table.add_column('学号')
        table.add_column('俯卧撑')
        table.add_column('仰卧起坐')
        table.add_column('引体向上')
        table.add_column('3000米跑')
        for record in result:
            table.add_row(*record)
        console.print(table)


def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


query = Query(username, password)

while True:
    print('1. 查 2. 增 3. 改 4. 删  5. 全部显示 6. 显示不及格\n其他键退出')
    # clear_console()
    match input():
        case '1':
            query.find(input('学号：'))
        case '2':
            query.add(input('学号：'), push_ups=input('俯卧撑：'), sit_ups=input('仰卧起坐：'),
                      pull_ups=input('引体向上：'), run_3000m=input('3000米跑：'))
        case '3':
            query.update(input('学号：'), push_ups=input('俯卧撑：'), sit_ups=input('仰卧起坐：'),
                         pull_ups=input('引体向上：'), run_3000m=input('3000米跑：'))
        case '4':
            query.delete(input('学号：'))
        case '5':
            query.show_all()
        case '6':
            query.show_failing_grade()
        case _:
            break

