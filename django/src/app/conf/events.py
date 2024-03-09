KAFKA_DRY_RUN = False
KAFKA_HOST = "localhost:9092"
KAFKA_REGISTRY_HOST = "localhost:8081"
KAFKA_CONSUME_TIMEOUT = 5.0


# TODO think about topic naming (from the feedback)
class Topics:
    """
    list of available topics to produce and consume
    """

    # tasks: CUD events
    tasks_stream = "tasks-stream"
    # tasks: business events
    tasks = "tasks"

    # users: CUD events
    users_stream = "users-stream"
    # users: business events
    users = "users"
