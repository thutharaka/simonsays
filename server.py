from flask import Flask, request, render_template, url_for, redirect
import time
from datetime import date
import asyncio
import threading
from script import get_ss
from state import SingletonState
from analyzer.analyzer import analyze

# Initialize variables in the server
app = Flask(__name__)

users = {
    "default": {
        "streak": 0,
        "health_points": 0,
        "last_completed_day": None
    }
}
daily_habits = [
    {"id": 1, "name": "Drink 1 Glass of Water"},
    {"id": 2, "name": "Sleep 8 Hours"},
    {"id": 3, "name": "Take a 5-Minute Walk"},
    {"id": 4, "name": "Stretch for 2 Minutes"}
]
completed_habits = set()

app_state = {
    "running": False,
    "start_time": None,
    "last_elapsed": None,
}

running = False
start_time = None
last_elapsed = None

tasks = []

singleton = SingletonState()

# Asynchronyous and periodic task to run in background
async def periodic_task():
    global singleton

    while singleton.get_state() != 'off':
        print("Task started")
        print('Task is running...')
        # get_ss()    # dummy fcn to rep sshot logic
        await asyncio.sleep(12)
        if singleton.get_state() != 'off':
            analyze(tasks)

def background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(periodic_task())

def start_task(name):
    return None

def on_start():
    return None

def on_stop():
    return None

@app.route("/")
def index():
    return redirect(url_for("home1"))

@app.route("/home1")
def home1():
    return render_template(
        "home1.html",
        running=app_state["running"],
        last_elapsed=app_state["last_elapsed"]
    )


@app.route("/goodluck", methods=["GET", "POST"])
def goodluck():
    name = None
    if request.method == "POST":
        name = request.form.get("task")
    return render_template("goodluck.html", name=name)


@app.route("/simonsays/")
def simonsays():
    return render_template("simonsays.html")


@app.route("/finish/")
def finish():
    return render_template("finish.html")


@app.route("/start", methods=["POST"])
def start():
    global running, start_time
    singleton.turn_on()
    t.start()
    if not running:
        running = True
        start_time = time.time()
        # start_task(task_name)
        # on_start()

    return redirect(url_for("goodluck"))


@app.route("/stop", methods=["POST"])
def stop():
    global running, start_time, last_elapsed
    singleton.turn_off()
    # try:
    #     loop.stop()
    # except Exception:
    #     print(f"Loop stopped")
    if running:
        running = False
        last_elapsed = time.time() - start_time
        # on_stop()

    return redirect(url_for("finish"))


@app.route("/taskinput")
def task_input():
    return render_template("home1.html")


@app.route("/save_task", methods=["POST"])
def save_task():
    # Server-side validation: strip whitespace and only save non-empty tasks
    task_raw = request.form.get("task", "")
    task = task_raw.strip()
    if task:
        tasks.append(task)
    # If the input was empty or whitespace only, ignore it and redirect.
    return redirect(url_for("dashboard"))

@app.route("/complete_habit/<int:habit_id>", methods=["POST"])
def complete_habit(habit_id):
    user = "default"

    if habit_id not in completed_habits:
        completed_habits.add(habit_id)
        users[user]["health_points"] += 5  # reward for completing habits

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    user = "default"
    return render_template(
        "dashboard.html",
        tasks=tasks,
        streak=users[user]["streak"],
        health_points=users[user]["health_points"],
        habits=daily_habits,
        completed=completed_habits
    )

loop = asyncio.new_event_loop()
t = threading.Thread(target=background_loop, args=(loop,))

if __name__ == "__main__":
    app.run(debug=True)
