import os
import threading
import json
import random
from twitchio.ext import commands
from dotenv import load_dotenv
from http.server import SimpleHTTPRequestHandler, HTTPServer

load_dotenv()

# CONFIG
CHANNEL = os.getenv('TWITCH_CHANNEL')
TOKEN = os.getenv('TWITCH_TOKEN')
MESSAGES_FILE = 'messages.json'
CHAT_HTML_FILE = 'chatbox.html'
CHAT_PORT = 8004

# Prepare the HTML page to only show the newest message, smoothly scrolling it once, then waiting for the next

def ensure_chat_html():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset='UTF-8'>
    <style>
    body { background: rgba(0,0,0,0); margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }
    .ticker-container {
        position: absolute;
        bottom: 40px;
        width: 100%;
        font-size: 28px;
        color: white;
        text-shadow: 2px 2px 4px #000;
        overflow: hidden;
        white-space: nowrap;
    }
    #ticker-content {
        display: inline-block;
        white-space: nowrap;
        transform: translateX(100%);
    }
    </style>
    <script>
    let lastMessage = '';
    let ticker = null;

    async function fetchMessages() {
        try {
            const res = await fetch('messages.json?_=' + new Date().getTime());
            const data = await res.json();
            if (data.new_message && data.new_message !== lastMessage) {
                lastMessage = data.new_message;
                showMessage(lastMessage);
            }
        } catch (err) { console.error(err); }
    }

    function showMessage(message) {
        const ticker = document.getElementById('ticker-content');
        ticker.innerHTML = message;
        ticker.style.transition = 'none';
        ticker.style.transform = 'translateX(100%)';
        void ticker.offsetWidth;
        ticker.style.transition = 'transform 10s linear';
        ticker.style.transform = 'translateX(-100%)';
    }

    setInterval(fetchMessages, 2000);
    window.onload = () => { ticker = document.getElementById('ticker-content'); fetchMessages(); };
    </script>
    </head>
    <body>
    <div class='ticker-container'>
        <div id='ticker-content'></div>
    </div>
    </body>
    </html>
    """
    with open(CHAT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

# Save only the newest message
def update_message_file(username, content):
    color = f'#{random.randint(0, 0xFFFFFF):06x}'
    formatted = f"<span style='color:{color};'>{username}</span>: {content}"
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump({'new_message': formatted}, f)

# Start local webserver
def start_chat_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', CHAT_PORT), handler)
    print(f"Serving chat overlay at http://localhost:{CHAT_PORT}/{CHAT_HTML_FILE}")
    httpd.serve_forever()

class ChatBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])

    async def event_ready(self):
        print(f'ChatBot logged in as | {self.nick}')
        ensure_chat_html()

    async def event_message(self, message):
        if message.echo:
            return
        update_message_file(message.author.name, message.content)

if __name__ == "__main__":
    ensure_chat_html()
    server_thread = threading.Thread(target=start_chat_server, daemon=True)
    server_thread.start()
    bot = ChatBot()
    bot.run()
