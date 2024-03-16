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
    tasks_dlq = "tasks-dlq"

    # users: CUD events
    users_stream = "users-stream"
    # users: business events
    users = "users"

    # billing: transactions CUD events
    billing_tx = "billing-tx"
    # billing: tasks CUD events (with costs)
    billing_tasks = "billing-tasks"
    billing_dlq = "billing-dlq"
