import os
import threading
import json
import random
import logging
from twitchio.ext import commands
from dotenv import load_dotenv
from http.server import SimpleHTTPRequestHandler, HTTPServer
from helpers import update_message_file



from hagrid_commands import HagridCommands

# Setup logger
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# CONFIG
CHANNEL = os.getenv('TWITCH_CHANNEL')
TOKEN = os.getenv('TWITCH_TOKEN')

print(f"Loaded TOKEN: {TOKEN}")
print(f"Loaded CHANNEL: {CHANNEL}")

MESSAGES_FILE = 'messages.json'
CHAT_HTML_FILE = 'chatbox.html'
CHAT_PORT = 8004

BOT_DISPLAY_NAME = "Hagrid"

message_queue = []

# Generate HTML overlay
def ensure_chat_html():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Comic+Neue&display=swap" rel="stylesheet">
        <meta charset='UTF-8'>
        <style>
            body, .thread-container {
                font-family: 'Comic Neue', sans-serif;
            }
            body { background: rgba(0,0,0,0); margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }
            .thread-container {
                position: absolute;
                bottom: 40px;
                width: 100%;
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: flex-start;
                font-size: 24px;
                color: white;
                text-shadow: 2px 2px 4px #000;
                overflow: hidden;
                white-space: nowrap;
                gap: 1.5rem;
                background-color: rgba(0, 0, 0, 0.6);
            }
            .message {
                flex-shrink: 0;
            }
        </style>
        <script>
        async function fetchMessages() {
            try {
                const res = await fetch('messages.json?_=' + new Date().getTime());
                const data = await res.json();
                const container = document.getElementById('thread-container');
                container.innerHTML = '';

                const maxWidth = container.offsetWidth;

                [...data.queue].reverse().forEach(msg => {
                    const temp = document.createElement('div');
                    temp.className = 'message';
                    temp.innerHTML = msg;
                    container.prepend(temp);

                    if (container.scrollWidth > maxWidth) {
                        temp.remove();  // remove if overflow
                    }
                });
            } catch (err) { console.error(err); }
        }

        setInterval(fetchMessages, 3000);
        window.onload = fetchMessages;
        </script>
    </head>
    <body>
    <div id='thread-container' class='thread-container'></div>
    </body>
    </html>
    """
    with open(CHAT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

# Save messages (keep last 50)
# def update_message_file(username, content):
#     color = f'#{random.randint(0, 0xFFFFFF):06x}'
#     formatted = f"<span style='color:{color};'>{username}</span>: {content}"
#     global message_queue
#     message_queue.append(formatted)
#     if len(message_queue) > 50:
#         message_queue = message_queue[-50:]
#     with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
#         json.dump({'queue': message_queue}, f)

# Start local webserver
def start_chat_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', CHAT_PORT), handler)
    print(f"Serving chat overlay at http://localhost:{CHAT_PORT}/{CHAT_HTML_FILE}")
    httpd.serve_forever()

sent_log = open('sent_responses.log', 'a', encoding='utf-8')

class ChatBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])

    async def event_ready(self):
        print(f'✅ ChatBot logged in as | {self.nick}')
        ensure_chat_html()

    async def event_message(self, message):
        if message.echo:
            return

        author = message.author.name.lower()
        content_raw = message.content
        content_clean = content_raw.strip().lower()

        update_message_file(message.author.name, message.content)

        allowed_greetings = ['salam', 'salaam', 'zalam', 'hi', 'hello', 'hey']

        if content_clean in allowed_greetings:
            sent_log.write(f"SENT: Salam, Khosh umadi  🪄❤️ triggered by '{content_clean}' from '{author}'\n")
            sent_log.flush()
            response = f'{BOT_DISPLAY_NAME}: Salam, Khosh umadi 🪄❤️'
            await message.channel.send(response)
            update_message_file(BOT_DISPLAY_NAME, 'Salam! Khosh umadi 🪄❤️')

        await self.handle_commands(message)  # allow handling !commands

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Hello, {ctx.author.name}! 👋')


if __name__ == "__main__":
    ensure_chat_html()
    server_thread = threading.Thread(target=start_chat_server, daemon=True)
    server_thread.start()

    bot = ChatBot()

    # Import and add Hagrid commands here
    from hagrid_commands import HagridCommands

    bot.add_cog(HagridCommands(bot))

    bot.run()
