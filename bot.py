import os
import re
import json
import random
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from twitchio.ext import commands
from dotenv import load_dotenv

load_dotenv()

CHANNEL = os.getenv('TWITCH_CHANNEL')
TOKEN = os.getenv('TWITCH_TOKEN')

TASKS_FILE = 'tasks.json'
MESSAGES_FILE = 'messages.json'

TASKS_HTML = 'tasks.html'
CHAT_HTML = 'chatbox.html'

TASKS_PORT = 8000
CHAT_PORT = 8004

message_queue = []
tasks_data = {}

# --------- TASK PART ---------
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def get_random_color():
    colors = ['#ff6f61', '#6a5acd', '#20b2aa', '#ffb347', '#87ceeb', '#ff69b4', '#98fb98', '#dda0dd']
    return random.choice(colors)

def update_tasks_html(tasks):
    html_parts = [
        "<!DOCTYPE html><html><head>",
        "<meta charset='UTF-8'>",
        "<style>",
        "body { background: rgba(0,0,0,0); margin: 0; padding: 0; font-family: 'Comic Neue', sans-serif; color: white; }",
        ".task-container { width: 400px; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 10px; }",
        ".header { font-size: 24px; font-weight: bold; margin-bottom: 10px; }",
        ".user-box { margin-bottom: 10px; padding: 5px; border: 1px solid white; border-radius: 5px; background: rgba(59,0,102,0.4); }",
        ".username { font-weight: bold; }",
        ".task { margin-left: 10px; }",
        ".done-task { margin-left: 10px; text-decoration: line-through; opacity: 0.6; }",
        "</style></head><body>",
        "<div class='task-container'><div class='header'>📋 Live Task Board</div>"
    ]

    for user, user_tasks in tasks.items():
        user_color = get_random_color()
        html_parts.append(f"<div class='user-box'><div class='username' style='color:{user_color};'>{user}</div>")
        for task in user_tasks:
            clean_task = task.replace('[DONE] ', '')
            if task.startswith('[DONE] '):
                html_parts.append(f"<div class='done-task'>• {clean_task}</div>")
            else:
                html_parts.append(f"<div class='task'>• {clean_task}</div>")
        html_parts.append("</div>")

    html_parts.append("</div></body></html>")

    with open(TASKS_HTML, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

# --------- CHAT PART ---------
def update_chat_html():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Comic+Neue&display=swap" rel="stylesheet">
    <style>
    body { background: rgba(0,0,0,0); margin: 0; padding: 0; font-family: 'Comic Neue', sans-serif; }
    .bar { position: absolute; bottom: 40px; width: 100%; display: flex; gap: 20px; font-size: 20px; color: white; text-shadow: 2px 2px 4px #000; background: rgba(0,0,0,0.4); padding: 5px; }
    .message { white-space: nowrap; }
    </style>
    <script>
    async function fetchMessages() {
        try {
            const res = await fetch('messages.json?_=' + new Date().getTime());
            const data = await res.json();
            const bar = document.getElementById('bar');
            bar.innerHTML = '';

            let totalWidth = 0;
            const maxWidth = bar.offsetWidth;

            [...data.queue].reverse().forEach(msg => {
                const temp = document.createElement('div');
                temp.className = 'message';
                temp.innerHTML = msg;
                bar.prepend(temp);

                if (bar.scrollWidth > maxWidth) {
                    temp.remove();
                }
            });
        } catch (err) { console.error(err); }
    }
    setInterval(fetchMessages, 3000);
    window.onload = fetchMessages;
    </script>
    </head><body>
    <div id="bar" class="bar"></div>
    </body></html>
    """
    with open(CHAT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

def update_message_file(username, content):
    color = f'#{random.randint(0, 0xFFFFFF):06x}'
    formatted = f"<span style='color:{color};'>{username}</span>: {content}"
    global message_queue
    message_queue.append(formatted)
    if len(message_queue) > 50:
        message_queue = message_queue[-50:]
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump({'queue': message_queue}, f)

# --------- SERVER PART ---------
def start_server(port):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)
    print(f"Serving on http://localhost:{port}/")
    httpd.serve_forever()

# --------- BOT ---------
class CombinedBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])
        global tasks_data
        tasks_data = load_tasks()
        update_tasks_html(tasks_data)
        update_chat_html()

        async def event_ready(self):
            print(f'✅ Logged in as {self.nick}')
            self.bot_name = self.nick.lower()

    async def event_ready(self):
        print(f'✅ Logged in as {self.nick}')

    async def event_message(self, message):
        if message.echo or message.author.name.lower() == self.bot_name:
            return

        content_lower = message.content.lower()
        print(f"[MESSAGE] {message.author.name}: {content_lower}")

        if re.search(r'sa+l+a+m+|za+l+a+m+|hi+i+|he+llo+|hallo+', content_lower):
            await message.channel.send('Salam! Khosh umadi 💜🪄')

        update_message_file(message.author.name, message.content)
        await self.handle_commands(message)

    @commands.command(name='task')
    async def task(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!task '):].strip()
        if not task_text:
            await ctx.send(f'{user}, please provide a task!')
            return
        tasks_data.setdefault(user, []).append(task_text)
        save_tasks(tasks_data)
        update_tasks_html(tasks_data)
        await ctx.send(f'{user}, I added your task: \"{task_text}\"')
        print(f"[TASK ADDED] {user}: {task_text}")

    @commands.command(name='done')
    async def done(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!done '):].strip()
        if user in tasks_data:
            for i, t in enumerate(tasks_data[user]):
                if t == task_text:
                    tasks_data[user][i] = f'[DONE] {task_text}'
                    save_tasks(tasks_data)
                    update_tasks_html(tasks_data)
                    await ctx.send(f'{user}, I marked your task as done: \"{task_text}\"')
                    print(f"[TASK DONE] {user}: {task_text}")
                    return
        await ctx.send(f'{user}, that task was not found.')

    @commands.command(name='remove')
    async def remove(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!remove '):].strip()
        if user in tasks_data and task_text in tasks_data[user]:
            tasks_data[user].remove(task_text)
            save_tasks(tasks_data)
            update_tasks_html(tasks_data)
            await ctx.send(f'{user}, I removed your task: \"{task_text}\"')
            print(f"[TASK REMOVED] {user}: {task_text}")
        else:
            await ctx.send(f'{user}, that task was not found.')

    @commands.command(name='delete')
    async def delete(self, ctx):
        user = ctx.author.name
        if user in tasks_data:
            del tasks_data[user]
            save_tasks(tasks_data)
            update_tasks_html(tasks_data)
            await ctx.send(f'{user}, I deleted your entire task box.')
            print(f"[TASK BOX DELETED] {user}")
        else:
            await ctx.send(f'{user}, you had no task box to delete.')

# --------- RUN ---------
if __name__ == "__main__":
    threading.Thread(target=start_server, args=(TASKS_PORT,), daemon=True).start()
    threading.Thread(target=start_server, args=(CHAT_PORT,), daemon=True).start()
    bot = CombinedBot()
    bot.run()
