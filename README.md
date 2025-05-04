# Hagrid The Guardian

A TwitchIO-based bot project coded in Python, designed to help manage Twitch chat, automate tasks, and bring some magic to your streams.

---

## 💻 Installation

1️⃣ Clone the repository:
```bash
git clone https://github.com/neg-is/HagridTheGuardian.git
2️⃣ Navigate into the project:

bash
Copy
Edit
cd HagridTheGuardian
3️⃣ Set up a virtual environment:

bash
Copy
Edit
python -m venv .venv
4️⃣ Activate the virtual environment:

On Windows:

bash
Copy
Edit
.venv\Scripts\activate
On macOS/Linux:

bash
Copy
Edit
source .venv/bin/activate
5️⃣ Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🚀 Usage
Run the bot:

bash
Copy
Edit
python chat_bot.py
Make sure your .env or token files are set up correctly (never upload these to GitHub!).

📂 Branches
Branch	Purpose
master	Stable, production-ready code
dev	Development work, new features, testing

👩‍💻 Contributors
Neg → Developer & Maintainer

📜 License
This project is licensed under the MIT License.

yaml
Copy
Edit

---

### 🛠 **Git Cheat Sheet**

✅ Initialize a local git repo  
```bash
git init
✅ Check current status

bash
Copy
Edit
git status
✅ Add all files

bash
Copy
Edit
git add .
✅ Commit changes

bash
Copy
Edit
git commit -m "Your message"
✅ Add a remote (once)

bash
Copy
Edit
git remote add origin https://github.com/neg-is/HagridTheGuardian.git
✅ Push local branch to GitHub

bash
Copy
Edit
git push -u origin master  # first push
git push                   # after first time
✅ Create a new branch

bash
Copy
Edit
git checkout -b dev
✅ Switch between branches

bash
Copy
Edit
git checkout master
git checkout dev
✅ Merge changes into master

bash
Copy
Edit
git checkout master
git merge dev
git push origin master
✅ Pull the latest changes from GitHub

bash
Copy
Edit
git pull
✅ See commit history

bash
Copy
Edit
git log
✅ Undo a staged file

bash
Copy
Edit
git reset HEAD <file>
✅ Discard local changes

bash
Copy
Edit
git checkout -- <file>
✅ See branches

bash
Copy
Edit
git branch
✅ Delete a branch

bash
Copy
Edit
git branch -d branchname
