import json
import os
import random
from twitchio.ext import commands
from dotenv import load_dotenv
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

load_dotenv()

# CONFIG
CHANNEL = os.getenv('TWITCH_CHANNEL')
TOKEN = os.getenv('TWITCH_TOKEN')
TASKS_FILE = 'tasks.json'
HTML_FILE = 'tasks.html'
PORT = 8000

# Adjustable layout sizes
OVERLAY_WIDTH = 1280
OVERLAY_HEIGHT = 720
TASK_AREA_WIDTH = 400
TASK_AREA_HEIGHT = 720

# Start local webserver
def start_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', PORT), handler)
    print(f"Serving at http://localhost:{PORT}/")
    httpd.serve_forever()

# Generate random color
def get_random_color():
    colors = ['#ff6f61', '#6a5acd', '#20b2aa', '#ffb347', '#87ceeb', '#ff69b4', '#98fb98', '#dda0dd']
    return random.choice(colors)

# Load and save tasks
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def update_html(tasks):
    html_parts = [
        "<!DOCTYPE html><html><head>",
        "<meta charset='UTF-8'>",
        "<meta http-equiv='refresh' content='5'>",  # Meta refresh every 5 seconds
        "<style>",
        f"body {{ background: rgba(0,0,0,0); margin: 0; padding: 0; width: {OVERLAY_WIDTH}px; height: {OVERLAY_HEIGHT}px; overflow: hidden; font-family: 'Segoe UI', sans-serif; color: white; }}",
        f".task-container {{ position: absolute; top: 0; left: 0; width: {TASK_AREA_WIDTH}px; height: {TASK_AREA_HEIGHT}px; overflow-y: scroll; padding: 10px; box-sizing: border-box; background: rgba(0,0,0,0.6); }}",
        f".user-box {{ border: 2px solid #fff; border-radius: 12px; padding: 8px; margin-bottom: 10px; box-shadow: 0 0 8px #000; }}",
        f".username {{ font-weight: bold; font-size: 20px; margin-bottom: 4px; }}",
        f".task {{ margin-left: 12px; margin-bottom: 3px; }}",
        f".done-task {{ margin-left: 12px; margin-bottom: 3px; text-decoration: line-through; opacity: 0.6; }}",
        "</style></head><body>",
        f"<div class='task-container'><h2>📝 Live Task Board</h2>"
    ]

    for user, user_tasks in tasks.items():
        user_color = get_random_color()
        html_parts.append(f'<div class="user-box" style="border-color: {user_color};"><div class="username" style="color: {user_color};">{user}</div>')
        for task in user_tasks:
            if task.startswith('[DONE] '):
                display_task = task.replace('[DONE] ', '')
                html_parts.append(f'<div class="done-task">• {display_task}</div>')
            else:
                html_parts.append(f'<div class="task">• {task}</div>')
        html_parts.append('</div>')

    html_parts.append("</div></body></html>")

    html = ''.join(html_parts)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

# Twitch bot setup for tasks only
class TaskBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.tasks = load_tasks()
        update_html(self.tasks)

    async def event_ready(self):
        print(f'TaskBot logged in as | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)
        update_html(self.tasks)

    @commands.command(name='task')
    async def task(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!task '):].strip()
        if not task_text:
            await ctx.send(f'{user}, please provide a task!')
            return
        self.tasks.setdefault(user, []).append(task_text)
        save_tasks(self.tasks)
        update_html(self.tasks)
        await ctx.send(f'{user}, I added your task: "{task_text}"')

    @commands.command(name='done')
    async def done(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!done '):].strip()
        if user in self.tasks:
            for i, t in enumerate(self.tasks[user]):
                if t == task_text:
                    self.tasks[user][i] = f'[DONE] {task_text}'
                    save_tasks(self.tasks)
                    update_html(self.tasks)
                    await ctx.send(f'{user}, I marked your task as done: "{task_text}"')
                    return
        await ctx.send(f'{user}, that task was not found.')

    @commands.command(name='clear')
    async def clear(self, ctx):
        user = ctx.author.name
        if user in self.tasks:
            del self.tasks[user]
            save_tasks(self.tasks)
            update_html(self.tasks)
            await ctx.send(f'{user}, I cleared all your tasks.')
        else:
            await ctx.send(f'{user}, you had no tasks to clear.')

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    bot = TaskBot()
    bot.run()

# → Separate chat_bot.py should handle only chat overlay, keeping the task bot focused and light.
