from os import path
import os.path
import random
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

TOKEN = ""
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}


def get_rand_str(length=10):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))


def make_request(endpoint, data, method="POST"):
    if method == "POST":
        response = requests.post(path.join(base_url, endpoint), headers=HEADERS, json=data)
    elif method == "PATCH":
        response = requests.patch(path.join(base_url, endpoint), headers=HEADERS, json=data)
    else:
        response = requests.get(path.join(base_url, endpoint), headers=HEADERS)

    response.raise_for_status()

    if response.status_code != 201:
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


def main():
    USERS_TO_CREATE = 1
    TASKS_TO_CREATE = 4
    TASKS_TO_COMPLETE = 3

    for _ in range(USERS_TO_CREATE):
        sleep(0.333)
        data = create_user()

    tasks_id = []
    for _ in range(TASKS_TO_CREATE):
        sleep(0.333)
        data = create_task()
        tasks_id.append(data["id"])

    sleep(0.5)
    for idx in random.choices(tasks_id, k=TASKS_TO_COMPLETE):
        sleep(0.333)
        data = complete_task(idx)
        print("completed task with id", idx)


if __name__ == "__main__":
    TOKEN = get_auth_token()

    print(f"got token {TOKEN[:5]}..")

    HEADERS.update({"Authorization": f"Bearer {TOKEN}"})

    main()

    # create_user()
    #
    # data = create_task()
    # sleep(0.5)
    # data = complete_task(data["id"])
