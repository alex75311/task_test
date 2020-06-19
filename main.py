from datetime import datetime
import os
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


def create_file(name, content):
    try:
        with open(os.path.join(DIR_NAME, name), 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError:
        os.remove(os.path.join(DIR_NAME, name))


def rename_file(name):
    with open(os.path.join(DIR_NAME, name), 'r', encoding='utf-8') as f:
        file_date = f.readline()

    file_date = file_date.split('> ')[1].strip()
    file_date = datetime.strptime(file_date, "%d.%m.%Y %H:%M")
    new_name = f'{name[:-4]}_{str(file_date)[:-3].replace(" ", "T").replace(":", ":")}.txt'
    if os.path.exists(os.path.join(DIR_NAME, new_name)):
        os.remove(os.path.join(DIR_NAME, new_name))
    os.rename(os.path.join(DIR_NAME, name), os.path.join(DIR_NAME, new_name))


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
            if os.path.exists(os.path.join(DIR_NAME, file_name)):
                rename_file(file_name)
            create_file(file_name, result_file)
