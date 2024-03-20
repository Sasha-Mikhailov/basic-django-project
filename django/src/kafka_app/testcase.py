from os import path
import os.path
import random
import sqlite3
from time import sleep
import uuid

import requests

django_host = "http://localhost:8000/"
api_prefix = "api/v1/"
base_url = path.join(django_host, api_prefix)

token_endpoint = "auth/token/"
users_endpoint = "users/"

tasks_endpoint = "tasks/"
reassign_endpoint = "tasks/reassign/"

billing_endpoint = "payments/"
cashout_endpoint = path.join(billing_endpoint, "cashout/")

TOKEN = ""
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}
DELAY = 0.333

SQLITE_DB_FILE = "src/db.sqlite"


def get_sqlite_conn():
    db_path = os.path.join(os.getcwd(), SQLITE_DB_FILE)
    conn = sqlite3.connect(db_path)
    return conn


def get_rand_str(length=10):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))


def make_request(endpoint, data=dict(), method="POST"):
    if method == "POST":
        response = requests.post(path.join(base_url, endpoint), headers=HEADERS, json=data)
    elif method == "PATCH":
        response = requests.patch(path.join(base_url, endpoint), headers=HEADERS, json=data)
    else:
        response = requests.get(path.join(base_url, endpoint), headers=HEADERS)

    response.raise_for_status()

    if response.status_code not in [200, 201]:
        print(response)
        return None

    return response.json()


def get_auth_token():
    global TOKEN
    global HEADERS

    data = {"username": "admin", "password": "admin"}
    response = make_request(token_endpoint, data)

    TOKEN = response["token"]

    return TOKEN


def create_user():
    data = {
        "username": f"worker_" + get_rand_str(5),
        "password": str(uuid.uuid4())[:8],
        # "role": "WORKER",
    }

    data = make_request(users_endpoint, data)

    print(f"created user `{data['username']}` with id {data['id']}, public_id ..{data['publicId'][-6:]}, role: {data['role']}")
    return data


def create_task():
    data = {
        "title": f"task_" + get_rand_str(5),
        "description": "Lorem Ipsum: " + get_rand_str(5),
    }

    data = make_request(tasks_endpoint, data)

    print(f"created task with id {data['id']}, `{data['title']}` public_id ..{data['publicId'][-6:]}, " f"status: {data['status']}, created: {data['created']}")
    return data


def complete_task(id: int):
    data = {
        "status": "COMPLETED",
    }
    endpoint = os.path.join(tasks_endpoint, str(id) + "/")
    data = make_request(endpoint, data, "PATCH")

    if data:
        print(
            f"completed task with id {data['id']}, `{data['title']}` public_id ..{data['publicId'][-6:]}, "
            f"status: {data['status']}, created: {data['created']}"
        )
        return data

    print(data)
    return None


def get_open_tasks(db_conn):
    ASSIGNED_TASKS_QUERY = """
        select id
        from tasks_task
        where status = 'ASSIGNED'
    """

    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute(ASSIGNED_TASKS_QUERY)
        ids = [res[0] for res in cursor.fetchall()]

    print(f"there are {len(ids)} open tasks")

    return ids


def complete_open_tasks(ids: list, all=False, k=2):
    if all:
        k = len(ids)
    else:
        k = int(len(ids) / k)  # complete some part of the tasks

    print(f"completing {k} tasks")
    for id in random.choices(ids, k=k):
        complete_task(id)
        print(f"completed task with id {id}")
        sleep(DELAY)


def reassign_tasks():
    data = make_request(reassign_endpoint, {})

    if data:
        print(f"reassigned tasks {data}")
        return data

    print(data)
    return None


def trigger_cashout():
    data = make_request(cashout_endpoint, {})

    if data:
        print(f"initiated cashout! got response: {data}")
        return data

    print(data)
    return data


def main():
    USERS_TO_CREATE = 0
    TASKS_TO_CREATE = 15
    TASKS_TO_COMPLETE = 13

    for _ in range(USERS_TO_CREATE):
        _ = create_user()
        sleep(DELAY)

    tasks_id = []
    for _ in range(TASKS_TO_CREATE):
        data = create_task()
        tasks_id.append(data["id"])
        sleep(DELAY)

    for idx in random.choices(tasks_id, k=TASKS_TO_COMPLETE):
        _ = complete_task(idx)
        print("completed task with id", idx)
        sleep(DELAY)


if __name__ == "__main__":
    TOKEN = get_auth_token()

    print(f"got token {TOKEN[:5]}..")

    HEADERS.update({"Authorization": f"Bearer {TOKEN}"})

    # main()

    # reassign_tasks()

    _ = trigger_cashout()


    # db_conn = get_sqlite_conn()
    #
    # ids = get_open_tasks(db_conn)
    #
    # complete_open_tasks(ids, all=True, k=2)

    # create_user()
    #
    # data = create_task()
    # sleep(0.5)
    # data = complete_task(data["id"])
