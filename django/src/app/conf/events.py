KAFKA_HOST = 'localhost:9092'


class Topics:
    """
    list of available topics to produce and consume
    """

    # tasks: CUD events
    tasks_stream = 'tasks-stream'
    # tasks: business events
    tasks = 'tasks'

    # users: CUD events
    users_stream = 'users-stream'
