import os
import json
import random
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()

CHANNEL = os.getenv('TWITCH_CHANNEL')
TOKEN = os.getenv('TWITCH_TOKEN')
MAX_MESSAGES = 5
CHAT_PORT = 8004
MESSAGES_FILE = 'messages.json'

message_queue = []

# --- Write initial empty file ---
with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
    json.dump({'queue': []}, f)

# --- Serve chat overlay ---
def start_server(port):
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)
    print(f"Serving on http://localhost:{port}/")
    httpd.serve_forever()

# --- Update messages file ---
def update_message_file(username, content):
    color = f'#{random.randint(0, 0xFFFFFF):06x}'
    formatted = f"<span style='color:{color};'>{username}</span>: {content}"
    global message_queue
    message_queue.append(formatted)
    if len(message_queue) > 50:
        message_queue = message_queue[-50:]
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump({'queue': message_queue}, f)
    print(f"[CHAT] Added: {username}: {content}")

# --- Bot ---
class ChatBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])

    async def event_ready(self):
        print(f'✅ Logged in as {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        update_message_file(message.author.name, message.content)
        await self.handle_commands(message)

# --- Generate HTML overlay ---
html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
body { background: transparent; margin: 0; font-family: sans-serif; color: white; }
#chat { display: flex; flex-direction: column; gap: 5px; font-size: 20px; }
</style>
<script>
async function updateChat() {
    try {
        const res = await fetch('messages.json?_=' + Date.now());
        const data = await res.json();
        const chat = document.getElementById('chat');
        chat.innerHTML = '';
        data.queue.slice(-""" + str(MAX_MESSAGES) + """).forEach(msg => {
            const div = document.createElement('div');
            div.innerHTML = msg;
            chat.appendChild(div);
        });
    } catch (err) {
        console.error('Fetch error:', err);
    }
}
setInterval(updateChat, 1000);
window.onload = updateChat;
</script>
</head>
<body>
<div id="chat"></div>
</body>
</html>
"""

with open('chatbox.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# --- Run ---
if __name__ == "__main__":
    threading.Thread(target=start_server, args=(CHAT_PORT,), daemon=True).start()
    bot = ChatBot()
    bot.run()