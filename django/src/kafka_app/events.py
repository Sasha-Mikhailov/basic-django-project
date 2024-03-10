from datetime import datetime
from time import sleep
import uuid


def get_base_event():
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": datetime.now().isoformat(),
    }


def get_event(
    event_name: str,
    event_version: int,
    producer: str,
    payload: dict,
):
    base_event = get_base_event()

    base_event.update(
        {
            "event_name": event_name,
            "event_version": event_version,
            "producer": producer,
            "payload": payload,
        }
    )

    return base_event


def event_producer(producer, **kwargs):
    def get_event_inner(
        producer: str = producer,
        event_name: str = None,
        event_version: int = None,
        payload: dict = None,
    ):
        base_event = get_base_event()

        base_event.update(
            {
                "event_name": event_name,
                "event_version": event_version,
                "producer": producer,
                "payload": payload,
            }
        )

        return base_event

    return get_event_inner


get_users_events = event_producer(producer="users-service")


if __name__ == "__main__":
    event1 = get_users_events(
        event_name="users.user-created",
        event_version=1,
        payload={
            "public_id": str(uuid.uuid4()),
        },
    )
    print(event1)

    sleep(1)

    event2 = get_users_events(
        event_name="users.user-created",
        event_version=1,
        payload={
            "public_id": str(uuid.uuid4()),
        },
    )
    print(event2)
