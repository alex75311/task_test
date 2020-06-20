from datetime import datetime
import os
from shutil import copyfile
import requests

URL_USER = 'https://json.medrating.org/users'
URL_TASK = 'https://json.medrating.org/todos'
DIR_NAME = 'tasks'


def create_dir(name):
    if os.path.exists(name):
        if not os.path.isdir(name):
            os.remove(name)
            os.mkdir(name)
    else:
        os.mkdir(name)


def get_users(url):
    try:
        users = requests.get(url).json()
        return users
    except Exception as e:
        print(e)
        exit(100)


def get_tasks(url):
    try:
        tasks = requests.get(url).json()
        return tasks
    except Exception as e:
        print(e)
        exit(100)


def pruning_length(lst: list, length=50):
    result = []
    for el in lst:
        if len(el) > length:
            result.append(el[:length] + '...')
        else:
            result.append(el)
    return result


def get_user_task(user_id: int, tasks: list):
    complete_tasks = []
    uncompleted_tasks = []
    task_idx = []

    for idx, task in enumerate(tasks):
        try:
            if task['userId'] == user_id:
                if task['completed']:
                    complete_tasks.append(task['title'])
                else:
                    uncompleted_tasks.append(task['title'])
                task_idx.append(idx)
        except KeyError:
            pass

    task_idx.reverse()
    for idx in task_idx:
        tasks.pop(idx)
    return complete_tasks, uncompleted_tasks


def create_file(name, back_name, content):
    try:
        with open(os.path.join(DIR_NAME, back_name), 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(e)
        os.remove(os.path.join(DIR_NAME, back_name))
    else:
        copyfile(os.path.join(DIR_NAME, back_name), os.path.join(DIR_NAME, name))


if __name__ == '__main__':
    create_dir(DIR_NAME)
    users = get_users(URL_USER)
    tasks = get_tasks(URL_TASK)
    if not users or not tasks:
        exit(100)
    for user in users:
        result_file = ''
        complete_tasks, uncompleted_tasks = get_user_task(user['id'], tasks)
        complete_tasks = pruning_length(complete_tasks)
        uncompleted_tasks = pruning_length(uncompleted_tasks)
        complete_tasks = '\n'.join(complete_tasks)
        uncompleted_tasks = '\n'.join(uncompleted_tasks)
        if complete_tasks or uncompleted_tasks:
            date = datetime.now().strftime("%d.%m.%Y %H:%M")
            result_file += f'''{user["name"]} <{user["email"]}> {date}
{user['company']['name']}

Завершённые задачи:
{complete_tasks}

Оставшиеся задачи:
{uncompleted_tasks}'''
            file_name = f'{user["username"]}.txt'
            file_back_name = f'{file_name[:-4]}_{str(date).replace(".", "-").replace(" ", "T").replace(":", "_")}.txt'
            create_file(file_name, file_back_name, result_file)
