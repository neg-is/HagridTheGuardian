import json
import random

message_queue = []
MESSAGES_FILE = 'messages.json'

def update_message_file(username, content):
    global message_queue
    color = f'#{random.randint(0, 0xFFFFFF):06x}'
    formatted = f"<span style='color:{color};'>{username}</span>: {content}"
    message_queue.append(formatted)
    if len(message_queue) > 50:
        message_queue = message_queue[-50:]
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump({'queue': message_queue}, f)
