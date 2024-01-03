import requests

print("学员体能考核成绩管理系统")
print(requests.post("http://127.0.0.1:5000/data",
                    data={'username': 'Teacher',
                          'password': 'password',
                          'account_name': 'Student',
                          'push_ups': '10',
                          'sit_ups': '10',
                          'pull_ups': '10',
                          'run_3000m': '10'}).text)
print(requests.get("http://127.0.0.1:5000/data", data={'username': 'Student',
                                                       'password': 'password', 'account_name': 'Student'}).text)
print(requests.delete("http://127.0.0.1:5000/data", data={'username': 'Teacher',
                                                          'password': 'password', 'account_name': 'Student'}).text)
print(requests.put("http://127.0.0.1:5000/data", data={'username': 'Teacher',
                                                       'password': 'password', 'account_name': 'Student',
                                                       'push_ups': '10', 'sit_ups': '10', 'pull_ups': '10',
                                                       'run_3000m': '114514'}).text)
print(requests.get("http://127.0.0.1:5000/get_all_data", data={'username': 'Teacher',
                                                               'password': 'password',
                                                               'column_name': 'pull_ups'}).json())
