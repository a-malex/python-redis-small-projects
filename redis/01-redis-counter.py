from flask import Flask
from redis import Redis

redis = Redis()

app = Flask(__name__)

old_counter = redis.getset("counter", "0").decode("utf-8")

@app.route("/")
def home():
    if redis.exists("counter"):
        redis.incr("counter")
        count = redis.get("counter").decode("utf-8")
        return f"counter is {count}"

@app.route("/stats")
def stats():
    if redis.exists("counter"):
        courent_count = redis.get("counter").decode("utf-8")
        return f"old counter is {old_counter} and current count is {courent_count}"
    
    
if __name__ == "__main__":
    Flask.run(app)