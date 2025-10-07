from connection import valkey_conn
from rq import Queue

queue = Queue("default", connection=valkey_conn)
