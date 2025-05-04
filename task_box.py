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

TASKS_FILE = 'tasks.json'
HTML_FILE = 'tasks.html'
PORT = 8000

# Adjustable layout sizes
OVERLAY_WIDTH = 1280
OVERLAY_HEIGHT = 720
TASK_AREA_WIDTH = 400
TASK_AREA_HEIGHT = 720

SCROLL_SPEED_PX_PER_SEC = 8

# Start local webserver
def start_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', PORT), handler)
    print(f"✅ Serving at http://localhost:{PORT}/tasks.html")
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
    total_boxes = sum(1 for user in tasks)
    total_height = total_boxes * 200
    visible_area = TASK_AREA_HEIGHT
    distance_to_scroll = max(total_height, visible_area)
    duration = distance_to_scroll / SCROLL_SPEED_PX_PER_SEC

    html_parts = [
        "<!DOCTYPE html><html><head>",
        "<meta charset='UTF-8'>",
        "<link href='https://fonts.googleapis.com/css2?family=Comic+Neue&display=swap' rel='stylesheet'>",
        "<style>",
        f"body {{ background: rgba(0,0,0,0); margin: 0; padding: 0; width: {OVERLAY_WIDTH}px; height: {OVERLAY_HEIGHT}px; overflow: hidden; font-family: 'Comic Neue', sans-serif; color: white; }}",
        f".task-container {{ position: absolute; top: 0; left: 0; width: {TASK_AREA_WIDTH}px; height: {TASK_AREA_HEIGHT}px; overflow: hidden; box-sizing: border-box; }}",
        f".header {{ font-size: 24px; font-weight: bold; padding: 10px; background: rgba(0,0,0,0.6); border-radius: 10px; margin-bottom: 5px; }}",
        f".scroll-content {{ display: flex; flex-direction: column; animation: scrollUp {duration}s linear infinite; }}",
        f".user-box {{ background: rgba(59, 0, 102, 0.3); backdrop-filter: blur(8px); border: 2px solid rgba(255, 255, 255, 0.3); border-radius: 12px; padding: 8px; margin: 8px 0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }}",
        f".username {{ font-weight: bold; font-size: 20px; margin-bottom: 4px; }}",
        f".task {{ margin-left: 12px; margin-bottom: 3px; }}",
        f".done-task {{ margin-left: 12px; margin-bottom: 3px; text-decoration: line-through; opacity: 0.6; }}",
        "@keyframes scrollUp {",
        "  0% { transform: translateY(0); }",
        "  100% { transform: translateY(-50%); }",
        "}",
        "</style></head><body>",
        "<div class='task-container'>",
        "<div class='header'>📝 Live Task Board</div>",
        "<div class='scroll-content'>"
    ]

    for user, user_tasks in tasks.items():
        user_color = get_random_color()
        html_parts.append(f"<div class='user-box' style='border-color:{user_color};'><div class='username' style='color:{user_color};'>{user}</div>")
        for task in user_tasks:
            clean_task = task.replace('[DONE] ', '')
            if task.startswith('[DONE] '):
                html_parts.append(f"<div class='done-task'>• {clean_task}</div>")
            else:
                html_parts.append(f"<div class='task'>• {clean_task}</div>")
        html_parts.append("</div>")  # Close user-box

    html_parts.append("</div></div></body></html>")

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

# Bot class
class TaskBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.tasks = load_tasks()

    async def event_ready(self):
        print(f"✅ TaskBot logged in as | {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

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
        await ctx.send(f'{user}, I added your task: \"{task_text}\"')

    @commands.command(name='done')
    async def done(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!done '):].strip()
        if user in self.tasks:
            for i, t in enumerate(self.tasks[user]):
                if t.strip().lower() == task_text.strip().lower():
                    self.tasks[user][i] = f'[DONE] {task_text}'
                    save_tasks(self.tasks)
                    update_html(self.tasks)
                    await ctx.send(f'{user}, I marked your task as done: \"{task_text}\"')
                    return
        await ctx.send(f'{user}, that task was not found.')

    @commands.command(name='remove')
    async def remove(self, ctx):
        user = ctx.author.name
        task_text = ctx.message.content[len('!remove '):].strip()
        if user in self.tasks and task_text in self.tasks[user]:
            self.tasks[user].remove(task_text)
            save_tasks(self.tasks)
            update_html(self.tasks)
            await ctx.send(f'{user}, I removed your task: \"{task_text}\"')
        else:
            await ctx.send(f'{user}, that task was not found.')

    @commands.command(name='delete')
    async def delete(self, ctx):
        user = ctx.author.name
        if user in self.tasks:
            del self.tasks[user]
            save_tasks(self.tasks)
            update_html(self.tasks)
            await ctx.send(f'{user}, I deleted your entire task box.')
        else:
            await ctx.send(f'{user}, you had no task box to delete.')

# Main
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    bot = TaskBot()
    bot.run()
