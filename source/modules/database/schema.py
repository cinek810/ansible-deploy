"""Sqlite database schema dictionaries"""

SCHEMAS = {
    "sequences": {
        "sequence_id": "text",
        "hostname": "text",
        "user_id": "text",
        "hooks": "text",
        "task": "text",
        "start": "text",
        "end": "text",
        "host_locked": "text",
        "keep_locked_on": "text",
        "self_setup_on": "text",
        "conf_dir_on": "text"
    },
    "play_item_tasks": {
        "sequence_id": "text",
        "timestamp": "text",
        "result": "text",
        "changed": "text",
        "hostname": "text",
        "task_name": "text"
    }
}
